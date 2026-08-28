"""Tests for the ADR check."""

from pathlib import Path

from repo_auditor.checks.adrs import check_adrs
from repo_auditor.models import CheckStatus


def test_adrs_passes(tmp_path: Path) -> None:
    """ADR check passes when an ADR exists."""

    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)

    (adr_dir / "0001-use-python.md").write_text(
        "# ADR 0001: Use Python",
        encoding="utf-8",
    )

    result = check_adrs(tmp_path)

    assert result.status == CheckStatus.PASS
    assert "ADR" in result.message


def test_adrs_passes_with_multiple_adrs(tmp_path: Path) -> None:
    """ADR check passes when multiple ADRs exist."""

    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)

    (adr_dir / "0001-first.md").write_text(
        "# ADR 0001",
        encoding="utf-8",
    )
    (adr_dir / "0002-second.md").write_text(
        "# ADR 0002",
        encoding="utf-8",
    )

    result = check_adrs(tmp_path)

    assert result.status == CheckStatus.PASS


def test_adrs_fails_when_directory_missing(tmp_path: Path) -> None:
    """ADR check fails when the ADR directory is missing."""

    result = check_adrs(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_adrs_fails_when_directory_is_empty(tmp_path: Path) -> None:
    """ADR check fails when the ADR directory is empty."""

    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)

    result = check_adrs(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_adrs_ignores_non_markdown_files(tmp_path: Path) -> None:
    """ADR check ignores non-Markdown files."""

    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)

    (adr_dir / "README.txt").write_text(
        "Not an ADR",
        encoding="utf-8",
    )

    result = check_adrs(tmp_path)

    assert result.status == CheckStatus.FAIL
