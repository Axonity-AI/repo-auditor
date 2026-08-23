"""Check that the repository has a non-empty LICENSE file."""

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
