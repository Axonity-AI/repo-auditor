"""CODEOWNERS audit check

CODEOWNERS configuration check.

This module verifies that the repository contains a non-empty CODEOWNERS
file.

The CODEOWNERS file defines the users or teams responsible for reviewing
changes to files in the repository.

The check passes when CODEOWNERS exists as a regular file and contains
content.

The check fails when the file is missing, empty, or when the expected
path is not a regular file.
"""

from pathlib import Path

from repo_auditor.models import CheckResult, CheckStatus


def check_codeowners(repo_path: Path) -> CheckResult:
    """Check that CODEOWNERS exists and is non-empty."""

    codeowners_path = repo_path / "CODEOWNERS"

    if not codeowners_path.is_file():
        return CheckResult(
            name="CODEOWNERS",
            status=CheckStatus.FAIL,
            message="CODEOWNERS file does not exist.",
        )

    if not codeowners_path.read_text(encoding="utf-8").strip():
        return CheckResult(
            name="CODEOWNERS",
            status=CheckStatus.FAIL,
            message="CODEOWNERS file is empty.",
        )

    return CheckResult(
        name="CODEOWNERS",
        status=CheckStatus.PASS,
        message="CODEOWNERS file exists and is non-empty.",
    )
