from __future__ import annotations

import string

from password_strength_checker.core.models import Finding, Policy, Severity
from password_strength_checker.core.rules.base import AbstractRule


class CharsetRule(AbstractRule):
    def check(self, password: str, policy: Policy) -> list[Finding]:
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in string.punctuation for c in password)

        classes = sum([has_lower, has_upper, has_digit, has_symbol])

        findings: list[Finding] = []
        if classes <= 1:
            findings.append(
                Finding(
                    "CHARSET_POOR",
                    "Très faible diversité (1 type de caractères).",
                    Severity.CRITICAL,
                    penalty=-30,
                    meta={"classes": classes},
                )
            )
        elif classes == 2:
            findings.append(
                Finding(
                    "CHARSET_LIMITED",
                    "Diversité limitée (2 types).",
                    Severity.WARNING,
                    penalty=-15,
                    meta={"classes": classes},
                )
            )
        else:
            findings.append(
                Finding(
                    "CHARSET_GOOD",
                    f"Bonne diversité ({classes} types).",
                    Severity.INFO,
                    penalty=0,
                    meta={"classes": classes},
                )
            )
        return findings
