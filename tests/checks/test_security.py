"""Tests for the SECURITY.md check."""

from pathlib import Path

from repo_auditor.checks.security import check_security
from repo_auditor.models import CheckStatus


def test_security_passes_when_file_exists_and_is_non_empty(tmp_path: Path) -> None:
    """SECURITY.md should pass when it exists and contains content."""
    security_path = tmp_path / "SECURITY.md"
    security_path.write_text("# Security Policy\n", encoding="utf-8")

    result = check_security(tmp_path)

    assert result.status == CheckStatus.PASS
    assert result.message == "SECURITY.md file exists and is non-empty."


def test_security_fails_when_file_does_not_exist(tmp_path: Path) -> None:
    """SECURITY.md should fail when it does not exist."""
    result = check_security(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == "SECURITY.md file does not exist."


def test_security_fails_when_file_is_empty(tmp_path: Path) -> None:
    """SECURITY.md should fail when it exists but is empty."""
    security_path = tmp_path / "SECURITY.md"
    security_path.write_text("", encoding="utf-8")

    result = check_security(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == "SECURITY.md file is empty."


def test_security_fails_when_path_is_directory(tmp_path: Path) -> None:
    """SECURITY.md should fail when the path is a directory."""
    (tmp_path / "SECURITY.md").mkdir()

    result = check_security(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == "SECURITY.md path is not a file."
