"""Check that the repository has a non-empty SECURITY.md file.


Security policy documentation check.

This module verifies that the repository contains a non-empty
`SECURITY.md` file.

The security policy provides a documented location and process for
reporting security vulnerabilities and handling security-related issues.

The check passes when SECURITY.md exists as a regular file and contains
content.

The check fails when the file is missing, empty, or when the expected
path is not a regular file.
"""

from pathlib import Path

from repo_auditor.models import CheckResult, CheckStatus


def check_security(repo_path: Path) -> CheckResult:
    """Check that SECURITY.md exists and is non-empty."""

    security_path = repo_path / "SECURITY.md"

    if not security_path.exists():
        return CheckResult(
            name="SECURITY",
            status=CheckStatus.FAIL,
            message="SECURITY.md file does not exist.",
        )

    if not security_path.is_file():
        return CheckResult(
            name="SECURITY",
            status=CheckStatus.FAIL,
            message="SECURITY.md path is not a file.",
        )

    if not security_path.read_text(encoding="utf-8").strip():
        return CheckResult(
            name="SECURITY",
            status=CheckStatus.FAIL,
            message="SECURITY.md file is empty.",
        )

    return CheckResult(
        name="SECURITY",
        status=CheckStatus.PASS,
        message="SECURITY.md file exists and is non-empty.",
    )
