"""Check that the repository has a non-empty LICENSE file

License file check.

This module verifies that the repository contains a non-empty LICENSE
file.

The license identifies the legal terms under which the repository's
software and source code can be used, modified, and distributed.

The check passes when LICENSE exists as a regular file and contains
content.

The check fails when the file is missing, empty, or when the expected
path is not a regular file.
"""

from pathlib import Path

from repo_auditor.models import CheckResult, CheckStatus


def check_license(repo_path: Path) -> CheckResult:
    """Check that LICENSE exists and is non-empty."""

    license_path = repo_path / "LICENSE"

    if not license_path.exists():
        return CheckResult(
            name="LICENSE",
            status=CheckStatus.FAIL,
            message="LICENSE file does not exist.",
        )

    if not license_path.is_file():
        return CheckResult(
            name="LICENSE",
            status=CheckStatus.FAIL,
            message="LICENSE path is not a file.",
        )

    if not license_path.read_text(encoding="utf-8").strip():
        return CheckResult(
            name="LICENSE",
            status=CheckStatus.FAIL,
            message="LICENSE file is empty.",
        )

    return CheckResult(
        name="LICENSE",
        status=CheckStatus.PASS,
        message="LICENSE file exists and is non-empty.",
    )
