from __future__ import annotations

from password_strength_checker.core.models import Finding, Policy, Severity
from password_strength_checker.core.rules.base import AbstractRule


class LengthRule(AbstractRule):
    def check(self, password: str, policy: Policy) -> list[Finding]:
        n = len(password)
        findings: list[Finding] = []
        if n < 8:
            findings.append(Finding("LEN_TOO_SHORT", "Moins de 8 caractères.", Severity.CRITICAL, penalty=-40))
        elif n < policy.min_length:
            findings.append(
                Finding(
                    "LEN_WEAK",
                    f"Longueur {n} < minimum recommandé ({policy.min_length}).",
                    Severity.WARNING,
                    penalty=-20,
                    meta={"length": n, "recommended": policy.min_length},
                )
            )
        elif n < policy.strong_length:
            findings.append(
                Finding(
                    "LEN_OK",
                    f"Longueur correcte ({n}), mais 16+ est idéal.",
                    Severity.INFO,
                    penalty=0,
                    meta={"length": n},
                )
            )
        else:
            findings.append(Finding("LEN_STRONG", f"Longueur forte ({n}).", Severity.INFO, penalty=0, meta={"length": n}))
        return findings
