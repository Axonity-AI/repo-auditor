"""CODEOWNERS audit check."""

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
