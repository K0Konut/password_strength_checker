from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path
from typing import List, Set

from .common import analyze_categories, count_categories, has_sequence, longest_repeat
from .models import CheckResult, Result


MIN_SCORE = 0
MAX_SCORE = 100


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
def load_dictionary_words() -> Set[str]:
    data_path = Path(__file__).resolve().parent.parent / "data" / "dictionary_words.txt"
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


def evaluate_password(password: str) -> Result:
    length = len(password)
    categories = analyze_categories(password)
    category_count = count_categories(password)
    sequence_found = has_sequence(password)
    repeat_len = longest_repeat(password)
    common_passwords = load_common_passwords()
    dictionary_words = load_dictionary_words()
    is_common = password.lower() in common_passwords if password else False
    has_dictionary_word = _contains_dictionary_word(password, dictionary_words)

    score = _length_score(length) + _diversity_bonus(category_count)

    if sequence_found:
        score -= 10
    if repeat_len >= 5:
        score -= 15
    elif repeat_len >= 3:
        score -= 8
    if is_common:
        score -= 25
    if has_dictionary_word:
        score -= 12

    if length < 8:
        score = min(score, 40)

    score = max(MIN_SCORE, min(MAX_SCORE, score))

    checks: List[CheckResult] = []
    if length >= 12:
        checks.append(CheckResult("length", True, "Longueur solide (>= 12)"))
    elif length >= 8:
        checks.append(CheckResult("length", True, "Longueur acceptable (8–11)"))
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

    if repeat_len >= 3:
        checks.append(CheckResult("repetition", False, "Répétitions détectées"))
    else:
        checks.append(CheckResult("repetition", True, "Pas de répétitions longues"))

    if is_common:
        checks.append(CheckResult("common", False, "Mot de passe trop commun"))
    else:
        checks.append(CheckResult("common", True, "Pas dans la liste des mots de passe communs"))

    if dictionary_words:
        if has_dictionary_word:
            checks.append(CheckResult("dictionary", False, "Mot du dictionnaire détecté"))
        else:
            checks.append(CheckResult("dictionary", True, "Pas de mots du dictionnaire évidents"))

    suggestions: List[str] = []
    if length < 12:
        suggestions.append("Augmenter la longueur à au moins 12 caractères")
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
    if repeat_len >= 3:
        suggestions.append("Éviter les répétitions (aaaa, 1111)")
    if is_common:
        suggestions.append("Éviter les mots de passe trop communs")
    if has_dictionary_word:
        suggestions.append("Éviter les mots du dictionnaire")

    if not suggestions:
        suggestions.append("Bon mot de passe : conserver cette diversité")

    entropy = _entropy_estimate(password)

    return Result(
        score=score,
        label=_label_for_score(score),
        checks=checks,
        suggestions=suggestions,
        entropy_estimate=entropy,
    )
