"""ADR repository check."""

from pathlib import Path

from repo_auditor.models import CheckResult, CheckStatus


def check_adrs(repo_path: Path) -> CheckResult:
    """Check that the repository contains an ADR directory with ADRs."""

    adr_dir = repo_path / "docs" / "adr"

    if not adr_dir.is_dir():
        return CheckResult(
            name="ADRs",
            status=CheckStatus.FAIL,
            message="Missing docs/adr directory.",
        )

    adr_files = list(adr_dir.glob("*.md"))

    if not adr_files:
        return CheckResult(
            name="ADRs",
            status=CheckStatus.FAIL,
            message="No ADR files found in docs/adr.",
        )

    return CheckResult(
        name="ADRs",
        status=CheckStatus.PASS,
        message=f"Found {len(adr_files)} ADR(s).",
    )
