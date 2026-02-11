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


def has_keyboard_sequence(password: str, min_len: int = 4) -> bool:
    if len(password) < min_len:
        return False

    rows = (
        "qwertyuiop",
        "asdfghjkl",
        "zxcvbnm",
        "azertyuiop",
        "qsdfghjklm",
        "wxcvbn",
    )

    pw = password.lower()
    for row in rows:
        for seq in (row, row[::-1]):
            index = {ch: idx for idx, ch in enumerate(seq)}
            run = 1
            for i in range(1, len(pw)):
                prev = pw[i - 1]
                curr = pw[i]
                if prev in index and curr in index:
                    diff = index[curr] - index[prev]
                    if diff == 1:
                        run += 1
                    else:
                        run = 1
                else:
                    run = 1
                if run >= min_len:
                    return True
    return False


def has_repeated_segment(password: str, min_len: int = 2, max_len: int = 4) -> bool:
    if len(password) < min_len * 2:
        return False

    pw = password.lower()
    max_len = min(max_len, len(pw) // 2)
    for size in range(min_len, max_len + 1):
        for i in range(len(pw) - size * 2 + 1):
            segment = pw[i : i + size]
            if segment == pw[i + size : i + size * 2]:
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
