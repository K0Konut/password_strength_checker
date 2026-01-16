from __future__ import annotations

from password_strength_checker.core.models import Finding, Policy, Severity
from password_strength_checker.core.rules.base import AbstractRule


class RepeatsRule(AbstractRule):
    def check(self, password: str, policy: Policy) -> list[Finding]:
        if not password:
            return []

        longest = 1
        run = 1
        for i in range(1, len(password)):
            if password[i] == password[i - 1]:
                run += 1
                longest = max(longest, run)
            else:
                run = 1

        if longest > policy.max_repeated_run:
            return [
                Finding(
                    "REPEAT_RUN",
                    f"Répétitions détectées (max run = {longest}).",
                    Severity.WARNING if longest <= 4 else Severity.CRITICAL,
                    penalty=-10 if longest <= 4 else -20,
                    meta={"max_run": longest},
                )
            ]
        return [Finding("REPEAT_OK", "Pas de répétitions excessives.", Severity.INFO, penalty=0)]
