from __future__ import annotations

from pathlib import Path

from password_strength_checker.core.models import Policy, Result
from password_strength_checker.core.rules.charset import CharsetRule
from password_strength_checker.core.rules.dictionary import DictionaryRule
from password_strength_checker.core.rules.length import LengthRule
from password_strength_checker.core.rules.repeats import RepeatsRule
from password_strength_checker.core.rules.sequences import SequencesRule
from password_strength_checker.core.scoring import compute_score, label_for
from password_strength_checker.core.estimates import estimate_times  # <-- IMPORTANT
from password_strength_checker.core.rules.banned import BannedWordsRule

def default_rules(data_dir: Path, policy: Policy) -> list[tuple[str, object]]:
    common_path = data_dir / "common_passwords.txt"
    rules: list[tuple[str, object]] = [
        ("length", LengthRule()),
        ("charset", CharsetRule()),
        ("repeats", RepeatsRule()),
        ("sequences", SequencesRule()),
        ("dictionary", DictionaryRule.from_file(common_path)),
        ("banned", BannedWordsRule()),
    ]

    # If enabled_rules empty => everything enabled
    if not policy.enabled_rules:
        return rules

    return [(name, rule) for name, rule in rules if policy.enabled_rules.get(name, True)]



def recommendations_from(result_score: int) -> list[str]:
    if result_score >= 85:
        return ["Rien à signaler. Évite juste la réutilisation sur plusieurs sites."]
    return [
        "Utilise 16+ caractères (idéalement une passphrase).",
        "Évite les suites (abcd/1234) et les répétitions (aaaa).",
        "Évite les mots du dictionnaire, prénoms, noms de marques, années.",
        "Mélange au moins 3 catégories (min/MAJ/chiffres/symboles) si possible.",
        "Utilise un gestionnaire de mots de passe pour générer/stocker.",
    ]


def evaluate(password: str, policy: Policy = Policy(), data_dir: Path | None = None) -> Result:
    data_dir = data_dir or Path(__file__).resolve().parents[1] / "data"

    findings = []
    for _, rule in default_rules(data_dir, policy):
        findings.extend(rule.check(password, policy))

    score = compute_score(password, findings)
    label = label_for(score)
    recs = recommendations_from(score)

    estimates = estimate_times(password, score, findings)  # <-- IMPORTANT

    return Result(
        score=score,
        label=label,
        findings=findings,
        recommendations=recs,
        estimates=estimates,  # <-- IMPORTANT
    )
