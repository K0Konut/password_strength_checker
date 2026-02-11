from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    message: str


@dataclass(frozen=True)
class Result:
    score: int
    label: str
    checks: List[CheckResult]
    suggestions: List[str]
    entropy_estimate: Optional[float] = None
