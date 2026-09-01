"""Tests for the pre-commit check."""

from pathlib import Path

from repo_auditor.checks.pre_commit import check_pre_commit
from repo_auditor.models import CheckStatus


def test_pre_commit_passes(tmp_path: Path) -> None:
    """Pre-commit check passes when configuration exists."""

    (tmp_path / ".pre-commit-config.yaml").write_text(
        """
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.12.0
    hooks:
      - id: ruff
""",
        encoding="utf-8",
    )

    result = check_pre_commit(tmp_path)

    assert result.status == CheckStatus.PASS


def test_pre_commit_fails_when_missing(tmp_path: Path) -> None:
    """Pre-commit check fails when configuration is missing."""

    result = check_pre_commit(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_pre_commit_fails_with_invalid_yaml(tmp_path: Path) -> None:
    """Pre-commit check fails when YAML is invalid."""

    (tmp_path / ".pre-commit-config.yaml").write_text(
        """
repos: [
invalid yaml
""",
        encoding="utf-8",
    )

    result = check_pre_commit(tmp_path)

    assert result.status == CheckStatus.FAIL
