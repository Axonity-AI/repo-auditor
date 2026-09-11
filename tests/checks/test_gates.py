from pathlib import Path

from repo_auditor.checks.gates import check_gates
from repo_auditor.models import CheckStatus


def test_gates_fails_when_workflows_directory_missing(tmp_path: Path) -> None:
    """Gates fail when the workflows directory is missing."""
    result = check_gates(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == "GitHub Actions workflows directory is missing."


def test_gates_ignores_non_workflow_files(tmp_path: Path) -> None:
    """Gates ignore files that are not YAML workflows."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "README.md").write_text(
        "Not a workflow.",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.PASS


def test_gates_ignores_invalid_yaml(tmp_path: Path) -> None:
    """Gates ignore workflows containing invalid YAML."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
jobs:
  test:
    steps:
      - run: [
""",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.PASS


def test_gates_ignores_non_dict_yaml(tmp_path: Path) -> None:
    """Gates ignore YAML that does not contain a mapping."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        "- pytest\n- ruff",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.PASS


def test_gates_ignores_non_dict_jobs(tmp_path: Path) -> None:
    """Gates ignore workflows whose jobs value is not a mapping."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  - pytest
""",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.PASS


def test_gates_ignores_non_dict_job(tmp_path: Path) -> None:
    """Gates ignore jobs that are not mappings."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  test: pytest
""",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.PASS


def test_gates_ignores_job_without_gate_command(tmp_path: Path) -> None:
    """Gates ignore jobs that do not contain a gate command."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "build"
""",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.PASS


def test_gates_ignores_non_list_steps(tmp_path: Path) -> None:
    """Gates ignore gate jobs whose steps value is not a list."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  test:
    runs-on: ubuntu-latest
    steps: pytest
""",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.PASS


def test_gates_ignores_non_dict_steps(tmp_path: Path) -> None:
    """Gates ignore individual steps that are not mappings."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - pytest
      - run: echo "done"
""",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.PASS


def test_gates_ignores_step_without_run_command(tmp_path: Path) -> None:
    """Gates ignore continue-on-error steps without a run command."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        continue-on-error: true
      - run: pytest
""",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.PASS


def test_gates_ignores_step_with_non_string_run(tmp_path: Path) -> None:
    """Gates ignore continue-on-error steps whose run value is not a string."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run:
          - pytest
        continue-on-error: true
""",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.PASS


def test_gates_ignores_gate_commands_outside_run_steps(tmp_path: Path) -> None:
    """Gate-like text outside run steps does not count as execution."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  test:
    runs-on: ubuntu-latest
    env:
      COMMAND: pytest
    steps:
      - run: echo "running tests"
""",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.PASS


def test_gates_detects_supported_gate_processes(tmp_path: Path) -> None:
    """Gates recognize supported lint, test, typecheck, and security processes."""
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
      - run: ruff check .
      - run: mypy src
      - run: gitleaks detect
      - run: tsc --noEmit
      - run: npm test
      - run: npm run test
      - run: black .
      - run: isort .
""",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.PASS


def test_gates_fails_when_gate_step_uses_continue_on_error(
    tmp_path: Path,
) -> None:
    """Gates fail when a recognized gate uses continue-on-error."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: black .
        continue-on-error: true
""",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == ("Gate step in job 'test' uses continue-on-error.")


def test_gates_fails_for_isort_continue_on_error(tmp_path: Path) -> None:
    """Gates fail when isort uses continue-on-error."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: isort .
        continue-on-error: true
""",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == ("Gate step in job 'test' uses continue-on-error.")


def test_gates_fails_when_job_uses_continue_on_error(
    tmp_path: Path,
) -> None:
    """Gates fail when a job containing a gate uses continue-on-error."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
jobs:
  test:
    runs-on: ubuntu-latest
    continue-on-error: true
    steps:
      - run: pytest
""",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.FAIL
    assert result.message == "Job 'test' uses continue-on-error."


def test_gates_does_not_treat_decorative_command_as_gate(
    tmp_path: Path,
) -> None:
    """A gate command mentioned in a job name should not count as a gate."""
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  test:
    name: Run pytest checks
    runs-on: ubuntu-latest
    steps:
      - run: echo "hello"
""",
        encoding="utf-8",
    )

    result = check_gates(tmp_path)

    assert result.status == CheckStatus.PASS
