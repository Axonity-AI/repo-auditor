"""Tests for the lint gate check."""

from pathlib import Path

from repo_auditor.checks.lint_gate import check_lint_gate
from repo_auditor.models import CheckStatus


def test_lint_gate_passes(tmp_path: Path) -> None:
    """Ruff command is present in a workflow."""

    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ruff check .
""",
        encoding="utf-8",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.PASS
    assert result.message == "CI includes a Ruff lint gate."


def test_lint_gate_fails_when_workflows_directory_missing(
    tmp_path: Path,
) -> None:
    """Missing workflows directory fails the check."""

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == "GitHub Actions workflows directory is missing."


def test_lint_gate_fails_when_ruff_is_missing(tmp_path: Path) -> None:
    """Workflow without Ruff fails the check."""

    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: pytest
""",
        encoding="utf-8",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == "No CI workflow runs Ruff."


def test_lint_gate_ignores_non_workflow_files(tmp_path: Path) -> None:
    """Non-YAML files are ignored."""

    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "README.md").write_text(
        "ruff check .",
        encoding="utf-8",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_ignores_invalid_yaml(tmp_path: Path) -> None:
    """Invalid YAML files are ignored."""

    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
jobs:
  lint:
    steps:
      - run: [invalid
""",
        encoding="utf-8",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_ignores_non_dict_yaml(tmp_path: Path) -> None:
    """YAML documents that are not mappings are ignored."""

    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        "- pytest\n- ruff",
        encoding="utf-8",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_ignores_non_dict_jobs(tmp_path: Path) -> None:
    """A jobs value that is not a mapping is ignored."""

    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  - lint
""",
        encoding="utf-8",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_ignores_non_dict_job(tmp_path: Path) -> None:
    """Jobs that are not mappings are ignored."""

    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  lint: pytest
""",
        encoding="utf-8",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_ignores_non_list_steps(tmp_path: Path) -> None:
    """A steps value that is not a list is ignored."""

    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  lint:
    steps:
      run: ruff check .
""",
        encoding="utf-8",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_ignores_non_dict_steps(tmp_path: Path) -> None:
    """Steps that are not mappings are ignored."""

    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  lint:
    steps:
      - pytest
      - 123
""",
        encoding="utf-8",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_ignores_non_string_run(tmp_path: Path) -> None:
    """A run value that is not a string is ignored."""

    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  lint:
    steps:
      - run:
          - ruff
""",
        encoding="utf-8",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL
