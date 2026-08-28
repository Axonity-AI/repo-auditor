"""Tests for the Conventional Commits check."""

from pathlib import Path

from repo_auditor.checks.conventional_commits import (
    check_conventional_commits,
)
from repo_auditor.models import CheckStatus


def test_conventional_commits_passes(tmp_path: Path) -> None:
    """Conventional Commits check passes when configured."""

    (tmp_path / ".pre-commit-config.yaml").write_text(
        """
repos:
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v4.2.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
""",
        encoding="utf-8",
    )

    result = check_conventional_commits(tmp_path)

    assert result.status == CheckStatus.PASS


def test_conventional_commits_fails_when_missing(tmp_path: Path) -> None:
    """Conventional Commits check fails when configuration is missing."""

    result = check_conventional_commits(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_conventional_commits_fails_without_commit_msg_hook(
    tmp_path: Path,
) -> None:
    """Check fails when no commit-msg hook is configured."""

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

    result = check_conventional_commits(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_conventional_commits_fails_with_invalid_yaml(
    tmp_path: Path,
) -> None:
    """Check fails when the pre-commit configuration is invalid."""

    (tmp_path / ".pre-commit-config.yaml").write_text(
        """
repos: [
invalid yaml
""",
        encoding="utf-8",
    )

    result = check_conventional_commits(tmp_path)

    assert result.status == CheckStatus.FAIL
