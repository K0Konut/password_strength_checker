from __future__ import annotations

from password_strength_checker.core.models import Finding


def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


def label_for(score: int) -> str:
    if score < 30:
        return "Very Weak"
    if score < 50:
        return "Weak"
    if score < 70:
        return "Fair"
    if score < 85:
        return "Strong"
    return "Very Strong"


def compute_score(password: str, findings: list[Finding]) -> int:
    n = len(password)

    # base score mainly from length
    if n >= 20:
        base = 90
    elif n >= 16:
        base = 80
    elif n >= 12:
        base = 65
    elif n >= 8:
        base = 45
    else:
        base = 20

    # penalties are negative in findings
    delta = sum(f.penalty for f in findings)

    # bonuses (kept out of findings to keep findings focused on "issues")
    codes = {f.code for f in findings}

    bonus = 0
    # If length is decent and charset diversity is good, bump up (common in pro checkers)
    if n >= 12 and "CHARSET_GOOD" in codes:
        bonus += 10

    # If already 16+ and charset good, small extra
    if n >= 16 and "CHARSET_GOOD" in codes:
        bonus += 5

    return clamp(base + delta + bonus, 0, 100)
