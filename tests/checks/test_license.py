"""Tests for the LICENSE check."""

from pathlib import Path

from repo_auditor.checks.license import check_license
from repo_auditor.models import CheckStatus


def test_license_passes_when_file_exists_and_is_non_empty(tmp_path: Path) -> None:
    """LICENSE should pass when it exists and contains content."""
    license_path = tmp_path / "LICENSE"
    license_path.write_text("MIT License\n", encoding="utf-8")

    result = check_license(tmp_path)

    assert result.status == CheckStatus.PASS
    assert result.message == "LICENSE file exists and is non-empty."


def test_license_fails_when_file_does_not_exist(tmp_path: Path) -> None:
    """LICENSE should fail when it does not exist."""
    result = check_license(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == "LICENSE file does not exist."


def test_license_fails_when_file_is_empty(tmp_path: Path) -> None:
    """LICENSE should fail when it exists but is empty."""
    license_path = tmp_path / "LICENSE"
    license_path.write_text("", encoding="utf-8")

    result = check_license(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == "LICENSE file is empty."


def test_license_fails_when_path_is_directory(tmp_path: Path) -> None:
    """LICENSE should fail when the path is a directory."""
    (tmp_path / "LICENSE").mkdir()

    result = check_license(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == "LICENSE path is not a file."
