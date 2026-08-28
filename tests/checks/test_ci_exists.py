"""Tests for the CI existence check."""

from pathlib import Path

from repo_auditor.checks.ci_exists import check_ci_exists
from repo_auditor.models import CheckStatus


def test_ci_exists_passes(tmp_path: Path) -> None:
    """CI check passes when a valid workflow exists."""

    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)

    (workflows_dir / "ci.yml").write_text(
        """
name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: pytest
""",
        encoding="utf-8",
    )

    result = check_ci_exists(tmp_path)

    assert result.status == CheckStatus.PASS


def test_ci_exists_fails_when_directory_missing(tmp_path: Path) -> None:
    """CI check fails when the workflows directory is missing."""

    result = check_ci_exists(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_ci_exists_fails_when_no_workflow_exists(tmp_path: Path) -> None:
    """CI check fails when no workflow exists."""

    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)

    result = check_ci_exists(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_ci_exists_fails_when_no_jobs_exist(tmp_path: Path) -> None:
    """CI check fails when a workflow has no jobs."""

    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)

    (workflows_dir / "ci.yml").write_text(
        """
name: CI
""",
        encoding="utf-8",
    )

    result = check_ci_exists(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_ci_exists_ignores_invalid_workflow(tmp_path: Path) -> None:
    """CI check fails when the workflow YAML is invalid."""

    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)

    (workflows_dir / "broken.yml").write_text(
        """
name: [
invalid yaml
""",
        encoding="utf-8",
    )

    result = check_ci_exists(tmp_path)

    assert result.status == CheckStatus.FAIL
