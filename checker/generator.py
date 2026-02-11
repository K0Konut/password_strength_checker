from __future__ import annotations

import secrets
from typing import List


def _build_pool(use_lower: bool, use_upper: bool, use_digit: bool, use_symbol: bool) -> list[str]:
    pool: list[str] = []
    if use_lower:
        pool.extend(list("abcdefghijklmnopqrstuvwxyz"))
    if use_upper:
        pool.extend(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    if use_digit:
        pool.extend(list("0123456789"))
    if use_symbol:
        pool.extend(list("!@#$%^&*()-_=+[]{};:,.?/"))
    return pool


def generate_passwords(
    *,
    length: int = 16,
    count: int = 1,
    use_lower: bool = True,
    use_upper: bool = True,
    use_digit: bool = True,
    use_symbol: bool = True,
) -> List[str]:
    if count < 1:
        raise ValueError("count must be >= 1")
    if not any([use_lower, use_upper, use_digit, use_symbol]):
        raise ValueError("at least one character category must be enabled")

    rng = secrets.SystemRandom()
    pool = _build_pool(use_lower, use_upper, use_digit, use_symbol)
    if not pool:
        raise ValueError("empty character pool")

    required: list[str] = []
    if use_lower:
        required.append(rng.choice(list("abcdefghijklmnopqrstuvwxyz")))
    if use_upper:
        required.append(rng.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")))
    if use_digit:
        required.append(rng.choice(list("0123456789")))
    if use_symbol:
        required.append(rng.choice(list("!@#$%^&*()-_=+[]{};:,.?/")))
    if length < len(required):
        raise ValueError("length too small for selected categories")

    passwords: List[str] = []
    for _ in range(count):
        chars = required[:]
        while len(chars) < length:
            chars.append(rng.choice(pool))
        rng.shuffle(chars)
        passwords.append("".join(chars))
    return passwords
