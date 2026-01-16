from __future__ import annotations

import string

from password_strength_checker.core.models import Finding, Policy, Severity
from password_strength_checker.core.rules.base import AbstractRule


def _has_sequence(s: str, k: int) -> bool:
    if k <= 1 or len(s) < k:
        return False

    # check ascending/descending sequences for letters and digits
    alph = string.ascii_lowercase
    digits = string.digits

    lower = s.lower()

    def scan(pool: str) -> bool:
        for i in range(len(pool) - k + 1):
            seq = pool[i : i + k]
            if seq in lower:
                return True
            if seq[::-1] in lower:
                return True
        return False

    return scan(alph) or scan(digits)


class SequencesRule(AbstractRule):
    def check(self, password: str, policy: Policy) -> list[Finding]:
        k = policy.forbid_sequences_len
        if _has_sequence(password, k):
            return [
                Finding(
                    "SEQUENCE",
                    f"Suite détectée (ex: 1234/abcd) sur {k}+ caractères.",
                    Severity.WARNING,
                    penalty=-15,
                    meta={"sequence_len": k},
                )
            ]
        return [Finding("SEQUENCE_OK", "Pas de suite simple détectée.", Severity.INFO, penalty=0)]
