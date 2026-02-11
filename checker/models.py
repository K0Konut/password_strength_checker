from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Union


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    message: str


@dataclass(frozen=True)
class ScoreBreakdown:
    length_score: int
    diversity_bonus: int
    penalties: Dict[str, int]
    capped: bool = False
    cap: Optional[int] = None
    cap_reason: Optional[str] = None


@dataclass(frozen=True)
class Result:
    score: int
    label: str
    checks: List[CheckResult]
    suggestions: List[str]
    entropy_estimate: Optional[float] = None
    length: int = 0
    category_count: int = 0
    min_length: int = 12
    score_breakdown: Optional[ScoreBreakdown] = None
    profile: str = "standard"
    ruleset_version: int = 2
    metrics: Optional[Dict[str, Union[int, bool]]] = None
