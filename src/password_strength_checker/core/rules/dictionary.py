from __future__ import annotations

from pathlib import Path

from password_strength_checker.core.models import Finding, Policy, Severity
from password_strength_checker.core.rules.base import AbstractRule


def _normalize(pw: str) -> str:
    # normalisation simple + "leet-lite"
    table = str.maketrans({"@": "a", "0": "o", "1": "l", "!": "i", "$": "s", "3": "e", "5": "s", "7": "t"})
    return pw.lower().translate(table)


class DictionaryRule(AbstractRule):
    def __init__(self, words: set[str]) -> None:
        self.words = words

    @classmethod
    def from_file(cls, path: Path) -> "DictionaryRule":
        words: set[str] = set()
        if path.exists():
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                w = line.strip().lower()
                if w and not w.startswith("#"):
                    words.add(w)
        return cls(words)

    def check(self, password: str, policy: Policy) -> list[Finding]:
        if not policy.forbid_dictionary:
            return []

        norm = _normalize(password)
        # match exact or contained long word
        if norm in self.words:
            return [Finding("DICT_EXACT", "Mot de passe dans une liste de mots de passe courants.", Severity.CRITICAL, penalty=-35)]
        for w in self.words:
            if len(w) >= 5 and w in norm:
                return [Finding("DICT_CONTAINS", f"Contient un mot courant: '{w}'.", Severity.WARNING, penalty=-20)]
        return [Finding("DICT_OK", "Pas de mot courant détecté.", Severity.INFO, penalty=0)]
