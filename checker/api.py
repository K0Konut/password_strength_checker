from __future__ import annotations

from typing import Iterable, List

from .models import Result
from .rules import evaluate_password
from .schema import json_schema


def evaluate(password: str, **kwargs) -> Result:
    return evaluate_password(password, **kwargs)


def evaluate_many(passwords: Iterable[str], **kwargs) -> List[Result]:
    return [evaluate_password(password, **kwargs) for password in passwords]


def get_json_schema() -> dict:
    return json_schema()
