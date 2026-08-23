"""Tests for the CODEOWNERS audit check."""

from pathlib import Path

from repo_auditor.checks.codeowners import check_codeowners
from repo_auditor.models import CheckStatus


def test_codeowners_passes_when_file_exists_and_is_non_empty(
    tmp_path: Path,
) -> None:
    """CODEOWNERS passes when the file exists and contains content."""

    (tmp_path / "CODEOWNERS").write_text(
        "* @axonity-ai",
        encoding="utf-8",
    )

    result = check_codeowners(tmp_path)

    assert result.status == CheckStatus.PASS
    assert result.message == "CODEOWNERS file exists and is non-empty."


def test_codeowners_fails_when_file_does_not_exist(
    tmp_path: Path,
) -> None:
    """CODEOWNERS fails when the file does not exist."""

    result = check_codeowners(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == "CODEOWNERS file does not exist."


def test_codeowners_fails_when_file_is_empty(
    tmp_path: Path,
) -> None:
    """CODEOWNERS fails when the file exists but is empty."""

    (tmp_path / "CODEOWNERS").write_text(
        "",
        encoding="utf-8",
    )

    result = check_codeowners(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == "CODEOWNERS file is empty."
