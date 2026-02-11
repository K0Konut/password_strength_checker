from __future__ import annotations

import hashlib
import urllib.error
import urllib.request
from functools import lru_cache
from pathlib import Path
from typing import Set


def _sha1_hex(password: str) -> str:
    return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()


@lru_cache(maxsize=4)
def load_breach_hashes(path: Path) -> Set[str]:
    hashes: Set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.strip().upper()
        if value and not value.startswith("#"):
            hashes.add(value)
    return hashes


def check_breach_list(password: str, path: Path) -> bool:
    if not password or not path.exists():
        return False
    sha1 = _sha1_hex(password)
    hashes = load_breach_hashes(path)
    return sha1 in hashes


def check_hibp_k_anonymity(password: str, *, timeout: float = 5.0) -> bool:
    if not password:
        return False
    sha1 = _sha1_hex(password)
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "password-strength-checker"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise RuntimeError("HIBP request failed") from exc
    for line in body.splitlines():
        if ":" not in line:
            continue
        hash_suffix, _count = line.split(":", 1)
        if hash_suffix.strip().upper() == suffix:
            return True
    return False
