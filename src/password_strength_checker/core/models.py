from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    severity: Severity
    penalty: int = 0  # negative reduces score
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Result:
    score: int
    label: str
    findings: list[Finding]
    recommendations: list[str]
    estimates: list[dict[str, object]] = field(default_factory=list)

    # NEW (pro)
    compliant: bool = True
    policy_violations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "label": self.label,
            "compliant": self.compliant,
            "policy_violations": self.policy_violations,
            "findings": [
                {
                    "code": f.code,
                    "message": f.message,
                    "severity": f.severity.value,
                    "penalty": f.penalty,
                    "meta": f.meta,
                }
                for f in self.findings
            ],
            "recommendations": self.recommendations,
            "estimates": self.estimates,
        }




@dataclass(frozen=True)
class Policy:
    min_length: int = 12
    strong_length: int = 16
    forbid_sequences_len: int = 4
    max_repeated_run: int = 2
    forbid_dictionary: bool = True

    # NEW (pro)
    min_classes: int = 3
    banned_words: list[str] = field(default_factory=list)
    enabled_rules: dict[str, bool] = field(default_factory=dict)
