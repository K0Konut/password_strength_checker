from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from password_strength_checker.core.models import Finding, Policy


class Rule(Protocol):
    def check(self, password: str, policy: Policy) -> list[Finding]: ...


class AbstractRule(ABC):
    @abstractmethod
    def check(self, password: str, policy: Policy) -> list[Finding]:
        raise NotImplementedError
