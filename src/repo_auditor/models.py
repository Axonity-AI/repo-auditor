from dataclasses import dataclass
from enum import Enum


class CheckStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    message: str
    details: str = ""
