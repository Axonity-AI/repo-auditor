"""
Core data models for repository audit results.

This module defines the status values and result structure shared by the
repository auditor and its individual checks.

CheckStatus represents the possible outcomes of an audit check:
pass, fail, warning, or not applicable.

CheckResult stores the result produced by a check, including its name,
status, human-readable message, and optional additional details.

Keeping these models centralized ensures that all checks return results
using the same structure and that the auditor, CLI, and output formatters
can process them consistently.
"""

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
