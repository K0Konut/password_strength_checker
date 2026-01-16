from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from password_strength_checker.core.models import Policy


def load_policy(path: Path) -> Policy:
    data = json.loads(path.read_text(encoding="utf-8"))
    # on garde seulement les champs connus
    allowed = {
    "min_length",
    "strong_length",
    "forbid_sequences_len",
    "max_repeated_run",
    "forbid_dictionary",
    "min_classes",
    "banned_words",
    "enabled_rules",
    }
    cleaned = {k: v for k, v in data.items() if k in allowed}
    return replace(Policy(), **cleaned)
