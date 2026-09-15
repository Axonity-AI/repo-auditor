"""Architecture Decision Records (ADR) repository check.

This module verifies that the repository contains an ADR directory at
`docs/adr` and that the directory contains at least one Markdown ADR.

ADR files document important architectural decisions, their context,
and the reasoning behind them.

The check passes when the ADR directory exists and contains one or more
Markdown files. Non-Markdown files are ignored.

The check fails when the ADR directory is missing or contains no
Markdown files.
"""

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
