from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path
from typing import List, Set

from .common import (
    analyze_categories,
    count_categories,
    has_keyboard_sequence,
    has_repeated_segment,
    has_sequence,
    longest_repeat,
)
from .models import CheckResult, Result, ScoreBreakdown


MIN_SCORE = 0
MAX_SCORE = 100

# Scoring rules (documented):
# - Length score uses _length_score thresholds:
#   <8: capped later, 8-11: ok, 12-15: good, 16+: very good
# - Diversity bonus: 2 categories +5, 3 categories +10, 4 categories +15
# - Penalties below are applied when patterns are detected
# - min_length only affects the "longueur solide" check and suggestions
SEQUENCE_PENALTY = 10
KEYBOARD_PENALTY = 10
REPEATED_SEGMENT_PENALTY = 10
REPEAT_PENALTY_MINOR = 8
REPEAT_PENALTY_MAJOR = 15
COMMON_PASSWORD_PENALTY = 25
DICTIONARY_PENALTY = 12


def _length_score(length: int) -> int:
    if length <= 0:
        return 0
    if length < 8:
        return min(length * 4, 28)
    if length <= 11:
        return 32 + (length - 8) * 4
    if length <= 15:
        return 48 + (length - 12) * 4
    return 64 + min(length - 16, 10) * 2


def _diversity_bonus(category_count: int) -> int:
    if category_count <= 1:
        return 0
    if category_count == 2:
        return 5
    if category_count == 3:
        return 10
    return 15


@lru_cache(maxsize=1)
def load_common_passwords() -> Set[str]:
    data_path = Path(__file__).resolve().parent.parent / "data" / "common_passwords.txt"
    if not data_path.exists():
        return set()

    common: Set[str] = set()
    for line in data_path.read_text(encoding="utf-8").splitlines():
        value = line.strip().lower()
        if value and not value.startswith("#"):
            common.add(value)
    return common


@lru_cache(maxsize=1)
def load_dictionary_words(path: Path | None = None) -> Set[str]:
    data_path = path or (Path(__file__).resolve().parent.parent / "data" / "dictionary_words.txt")
    if not data_path.exists():
        return set()

    words: Set[str] = set()
    for line in data_path.read_text(encoding="utf-8").splitlines():
        value = line.strip().lower()
        if value and not value.startswith("#"):
            words.add(value)
    return {word for word in words if len(word) >= 4}


def _contains_dictionary_word(password: str, words: Set[str]) -> bool:
    if not password or not words:
        return False

    lowered = password.lower()
    for word in words:
        if word in lowered:
            return True
    return False


def _entropy_estimate(password: str) -> float | None:
    if not password:
        return None

    categories = analyze_categories(password)
    pool = 0
    if categories["lower"]:
        pool += 26
    if categories["upper"]:
        pool += 26
    if categories["digit"]:
        pool += 10
    if categories["symbol"]:
        pool += 32

    if pool <= 0:
        return None

    return round(len(password) * math.log2(pool), 2)


def _label_for_score(score: int) -> str:
    if score < 30:
        return "Faible"
    if score < 60:
        return "Moyen"
    if score < 80:
        return "Fort"
    return "Très fort"


def evaluate_password(
    password: str,
    *,
    min_length: int = 12,
    use_dictionary: bool = True,
    dictionary_path: Path | None = None,
) -> Result:
    length = len(password)
    min_length = max(8, min_length)
    if dictionary_path is not None and not isinstance(dictionary_path, Path):
        dictionary_path = Path(dictionary_path)
    categories = analyze_categories(password)
    category_count = count_categories(password)
    sequence_found = has_sequence(password)
    keyboard_sequence = has_keyboard_sequence(password)
    repeated_segment = has_repeated_segment(password)
    repeat_len = longest_repeat(password)
    common_passwords = load_common_passwords()
    dictionary_words = load_dictionary_words(dictionary_path) if use_dictionary else set()
    is_common = password.lower() in common_passwords if password else False
    has_dictionary_word = _contains_dictionary_word(password, dictionary_words)

    length_score = _length_score(length)
    diversity_bonus = _diversity_bonus(category_count)
    score = length_score + diversity_bonus
    penalties: dict[str, int] = {}

    if sequence_found:
        penalties["sequence"] = SEQUENCE_PENALTY
        score -= SEQUENCE_PENALTY
    if keyboard_sequence:
        penalties["keyboard"] = KEYBOARD_PENALTY
        score -= KEYBOARD_PENALTY
    if repeated_segment:
        penalties["pattern"] = REPEATED_SEGMENT_PENALTY
        score -= REPEATED_SEGMENT_PENALTY
    if repeat_len >= 5:
        penalties["repetition"] = REPEAT_PENALTY_MAJOR
        score -= REPEAT_PENALTY_MAJOR
    elif repeat_len >= 3:
        penalties["repetition"] = REPEAT_PENALTY_MINOR
        score -= REPEAT_PENALTY_MINOR
    if is_common:
        penalties["common"] = COMMON_PASSWORD_PENALTY
        score -= COMMON_PASSWORD_PENALTY
    if has_dictionary_word:
        penalties["dictionary"] = DICTIONARY_PENALTY
        score -= DICTIONARY_PENALTY

    capped = False
    cap_value: int | None = None
    cap_reason: str | None = None
    if length < 8:
        capped = True
        cap_value = 40
        cap_reason = "Longueur < 8"
        score = min(score, cap_value)

    score = max(MIN_SCORE, min(MAX_SCORE, score))

    checks: List[CheckResult] = []
    if length >= min_length:
        checks.append(CheckResult("length", True, f"Longueur solide (>= {min_length})"))
    elif length >= 8:
        checks.append(
            CheckResult(
                "length",
                True,
                f"Longueur acceptable (>= 8, < {min_length})",
            )
        )
    else:
        checks.append(CheckResult("length", False, "Mot de passe trop court (< 8)"))

    if category_count >= 3:
        checks.append(CheckResult("diversity", True, "Diversité de caractères suffisante"))
    else:
        missing = [
            name
            for name, present in categories.items()
            if not present
        ]
        checks.append(
            CheckResult(
                "diversity",
                False,
                "Catégories manquantes: " + ", ".join(missing),
            )
        )

    if sequence_found:
        checks.append(CheckResult("sequence", False, "Suites détectées (ex: abcd, 1234)"))
    else:
        checks.append(CheckResult("sequence", True, "Pas de suites évidentes"))

    if keyboard_sequence:
        checks.append(CheckResult("keyboard", False, "Suites clavier détectées (ex: qwerty, azerty)"))
    else:
        checks.append(CheckResult("keyboard", True, "Pas de suites clavier évidentes"))

    if repeated_segment:
        checks.append(CheckResult("pattern", False, "Motif répété détecté (ex: abcabc, 1212)"))
    else:
        checks.append(CheckResult("pattern", True, "Pas de motifs répétés"))

    if repeat_len >= 3:
        checks.append(CheckResult("repetition", False, "Répétitions détectées"))
    else:
        checks.append(CheckResult("repetition", True, "Pas de répétitions longues"))

    if is_common:
        checks.append(CheckResult("common", False, "Mot de passe trop commun"))
    else:
        checks.append(CheckResult("common", True, "Pas dans la liste des mots de passe communs"))

    if use_dictionary and dictionary_words:
        if has_dictionary_word:
            checks.append(CheckResult("dictionary", False, "Mot du dictionnaire détecté"))
        else:
            checks.append(CheckResult("dictionary", True, "Pas de mots du dictionnaire évidents"))

    suggestions: List[str] = []
    if length < min_length:
        suggestions.append(f"Augmenter la longueur à au moins {min_length} caractères")
    if not categories["lower"]:
        suggestions.append("Ajouter des minuscules")
    if not categories["upper"]:
        suggestions.append("Ajouter des majuscules")
    if not categories["digit"]:
        suggestions.append("Ajouter des chiffres")
    if not categories["symbol"]:
        suggestions.append("Ajouter des symboles")
    if sequence_found:
        suggestions.append("Éviter les suites évidentes (abcd, 1234)")
    if keyboard_sequence:
        suggestions.append("Éviter les suites clavier (qwerty, azerty)")
    if repeated_segment:
        suggestions.append("Éviter les motifs répétés (abcabc, 1212)")
    if repeat_len >= 3:
        suggestions.append("Éviter les répétitions (aaaa, 1111)")
    if is_common:
        suggestions.append("Éviter les mots de passe trop communs")
    if has_dictionary_word:
        suggestions.append("Éviter les mots du dictionnaire")

    if not suggestions:
        suggestions.append("Bon mot de passe : conserver cette diversité")

    entropy = _entropy_estimate(password)
    breakdown = ScoreBreakdown(
        length_score=length_score,
        diversity_bonus=diversity_bonus,
        penalties=penalties,
        capped=capped,
        cap=cap_value,
        cap_reason=cap_reason,
    )

    return Result(
        score=score,
        label=_label_for_score(score),
        checks=checks,
        suggestions=suggestions,
        entropy_estimate=entropy,
        length=length,
        category_count=category_count,
        min_length=min_length,
        score_breakdown=breakdown,
    )
