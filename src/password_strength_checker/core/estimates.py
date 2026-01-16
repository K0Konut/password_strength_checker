from __future__ import annotations
from password_strength_checker.core.models import Finding

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class CrackScenario:
    name: str
    guesses_per_second: float


DEFAULT_SCENARIOS = [
    CrackScenario("Online (throttled ~10/s)", 10.0),
    CrackScenario("Online (unthrottled ~1k/s)", 1_000.0),
    CrackScenario("Offline (fast hash GPU ~1e10/s)", 1e10),
    CrackScenario("Offline (slow hash ~1e4/s)", 10_000.0),
]


def _format_seconds(seconds: float) -> str:
    if seconds < 1:
        return "< 1s"
    units = [
        ("s", 60),
        ("min", 60),
        ("h", 24),
        ("d", 365),
        ("y", 1000),
    ]
    v = seconds
    for unit, base in units:
        if v < base:
            return f"~{v:.1f}{unit}" if v < 10 else f"~{v:.0f}{unit}"
        v /= base
    return "~1000y+"


def estimate_keyspace(password: str) -> int:
    """
    Keyspace approximation based on character classes present.
    This is intentionally conservative and later penalized by findings/patterns.
    """
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_other = any((not c.isalnum()) for c in password)

    alphabet = 0
    if has_lower:
        alphabet += 26
    if has_upper:
        alphabet += 26
    if has_digit:
        alphabet += 10
    if has_other:
        # approximate printable symbols
        alphabet += 33

    if alphabet <= 1:
        alphabet = 1

    return int(alphabet ** len(password))


def estimate_times(password: str, score: int, findings: list[Finding], scenarios=DEFAULT_SCENARIOS) -> list[dict[str, str]]:
    """
    Convert score + keyspace into rough crack-time estimates.
    We use a conservative adjustment factor based on score.
    """
    keyspace = estimate_keyspace(password)

    # Score-based factor (rough)
    factor = 10 ** ((score - 100) / 20)

    # Findings-based multiplier (patterns/dictionary)
    mult = effective_space_multiplier(findings)

    effective = max(1, int(keyspace * factor * mult))


    out: list[dict[str, str]] = []
    for s in scenarios:
        seconds = effective / s.guesses_per_second
        out.append(
            {
                "scenario": s.name,
                "guesses_per_second": f"{s.guesses_per_second:.3g}",
                "time": _format_seconds(seconds),
                "seconds": seconds,  # <-- AJOUT
            }
        )

    return out

def effective_space_multiplier(findings: list[Finding]) -> float:
    """
    If common patterns are detected, attackers don't brute-force the whole space.
    We shrink the effective search space aggressively.
    """
    codes = {f.code for f in findings}

    mult = 1.0

    # Dictionary hits are devastating
    if "DICT_EXACT" in codes:
        mult *= 1e-12
    elif "DICT_CONTAINS" in codes:
        mult *= 1e-8

    # Common sequences reduce greatly
    if "SEQUENCE" in codes:
        mult *= 1e-6

    # Repeats reduce some
    if "REPEAT_RUN" in codes:
        mult *= 1e-3

    # clamp
    return max(mult, 1e-15)
