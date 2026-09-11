"""Tests for the process-based lint gate check."""

from pathlib import Path

from repo_auditor.checks.lint_gate import check_lint_gate
from repo_auditor.models import CheckStatus


def _create_workflow(tmp_path: Path, content: str) -> None:
    """Create a GitHub Actions workflow for testing."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text(content, encoding="utf-8")


def test_lint_gate_passes_with_ruff(tmp_path: Path) -> None:
    """A Ruff command satisfies the linting process."""
    _create_workflow(
        tmp_path,
        """
jobs:
  quality:
    steps:
      - run: ruff check .
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.PASS
    assert result.message == "CI includes a linting gate."


def test_lint_gate_passes_with_equivalent_lint_command(tmp_path: Path) -> None:
    """An equivalent lint command satisfies the linting process."""
    _create_workflow(
        tmp_path,
        """
jobs:
  quality:
    steps:
      - run: npm run lint
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.PASS


def test_lint_gate_passes_with_make_lint(tmp_path: Path) -> None:
    """A make lint command satisfies the linting process."""
    _create_workflow(
        tmp_path,
        """
jobs:
  quality:
    steps:
      - run: make lint
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.PASS


def test_lint_gate_passes_with_lint_script(tmp_path: Path) -> None:
    """A dedicated lint script satisfies the linting process."""
    _create_workflow(
        tmp_path,
        """
jobs:
  quality:
    steps:
      - run: ./scripts/lint.sh
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.PASS


def test_lint_gate_passes_when_lint_runs_after_other_commands(
    tmp_path: Path,
) -> None:
    """A lint process following another command is detected."""
    _create_workflow(
        tmp_path,
        """
jobs:
  quality:
    steps:
      - run: npm install && npm run lint
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.PASS


def test_lint_gate_fails_without_linting(tmp_path: Path) -> None:
    """A workflow without a linting process fails."""
    _create_workflow(
        tmp_path,
        """
jobs:
  test:
    steps:
      - run: pytest
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == "No CI workflow performs linting."


def test_lint_gate_does_not_accept_echo_as_linting(tmp_path: Path) -> None:
    """Mentioning lint in an echo command does not satisfy the gate."""
    _create_workflow(
        tmp_path,
        """
jobs:
  build:
    steps:
      - run: echo "lint is not run here"
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_does_not_accept_job_name_alone(tmp_path: Path) -> None:
    """A job named lint is not enough without an executable process."""
    _create_workflow(
        tmp_path,
        """
jobs:
  lint:
    steps:
      - run: echo "hello"
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_does_not_accept_installing_linter(tmp_path: Path) -> None:
    """Installing a linting package is not itself a linting process."""
    _create_workflow(
        tmp_path,
        """
jobs:
  setup:
    steps:
      - run: npm install eslint
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_fails_when_workflows_directory_missing(
    tmp_path: Path,
) -> None:
    """A missing workflows directory fails the check."""
    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == "GitHub Actions workflows directory is missing."


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
    _create_workflow(
        tmp_path,
        """
jobs:
  lint:
    steps:
      - run: [invalid
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_ignores_non_dict_yaml(tmp_path: Path) -> None:
    """Non-mapping YAML documents are ignored."""
    _create_workflow(
        tmp_path,
        """
- ruff
- pytest
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_ignores_non_dict_jobs(tmp_path: Path) -> None:
    """A non-mapping jobs value is ignored."""
    _create_workflow(
        tmp_path,
        """
jobs:
  - lint
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_ignores_non_dict_job(tmp_path: Path) -> None:
    """A non-mapping job is ignored."""
    _create_workflow(
        tmp_path,
        """
jobs:
  lint: pytest
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_ignores_non_list_steps(tmp_path: Path) -> None:
    """A non-list steps value is ignored."""
    _create_workflow(
        tmp_path,
        """
jobs:
  lint:
    steps:
      run: ruff check .
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_ignores_non_dict_steps(tmp_path: Path) -> None:
    """Non-mapping steps are ignored."""
    _create_workflow(
        tmp_path,
        """
jobs:
  lint:
    steps:
      - pytest
      - 123
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_lint_gate_ignores_non_string_run(tmp_path: Path) -> None:
    """A non-string run value is ignored."""
    _create_workflow(
        tmp_path,
        """
jobs:
  lint:
    steps:
      - run:
          - ruff
""",
    )

    result = check_lint_gate(tmp_path)

    assert result.status == CheckStatus.FAIL
