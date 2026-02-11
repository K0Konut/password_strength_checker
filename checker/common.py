from __future__ import annotations

from typing import Dict


def analyze_categories(password: str) -> Dict[str, bool]:
    return {
        "lower": any(ch.islower() for ch in password),
        "upper": any(ch.isupper() for ch in password),
        "digit": any(ch.isdigit() for ch in password),
        "symbol": any(not ch.isalnum() for ch in password),
    }


def count_categories(password: str) -> int:
    categories = analyze_categories(password)
    return sum(1 for present in categories.values() if present)


def has_sequence(password: str, min_len: int = 4) -> bool:
    if len(password) < min_len:
        return False

    pw = password.lower()
    run = 1
    for i in range(1, len(pw)):
        prev = pw[i - 1]
        curr = pw[i]

        if prev.isalpha() and curr.isalpha():
            diff = ord(curr) - ord(prev)
            if diff in (1, -1):
                run += 1
            else:
                run = 1
        elif prev.isdigit() and curr.isdigit():
            diff = ord(curr) - ord(prev)
            if diff in (1, -1):
                run += 1
            else:
                run = 1
        else:
            run = 1

        if run >= min_len:
            return True

    return False


def longest_repeat(password: str) -> int:
    if not password:
        return 0

    max_run = 1
    run = 1
    for i in range(1, len(password)):
        if password[i] == password[i - 1]:
            run += 1
        else:
            run = 1
        if run > max_run:
            max_run = run

    return max_run
