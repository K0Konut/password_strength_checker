from __future__ import annotations

from password_strength_checker.core.models import Finding, Policy, Severity
from password_strength_checker.core.rules.base import AbstractRule


class BannedWordsRule(AbstractRule):
    def check(self, password: str, policy: Policy) -> list[Finding]:
        if not policy.banned_words:
            return []

        pw_lower = password.lower()
        for w in policy.banned_words:
            ww = w.strip().lower()
            if ww and ww in pw_lower:
                return [
                    Finding(
                        "BANNED_WORD",
                        f"Contient un mot interdit par la policy: '{w}'.",
                        Severity.CRITICAL,
                        penalty=-40,
                        meta={"word": w},
                    )
                ]
        return []
