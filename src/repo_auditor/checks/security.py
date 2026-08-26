"""Check that the repository has a non-empty SECURITY.md file."""

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
