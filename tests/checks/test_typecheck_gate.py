from pathlib import Path

from repo_auditor.checks.typecheck_gate import check_typecheck_gate
from repo_auditor.models import CheckStatus


def test_typecheck_gate_passes_with_tsc(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - run: tsc --noEmit
""",
        encoding="utf-8",
    )

    result = check_typecheck_gate(tmp_path)

    assert result.status == CheckStatus.PASS


def test_typecheck_gate_ignores_non_workflow_files(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "README.md").write_text(
        "mypy src",
        encoding="utf-8",
    )

    result = check_typecheck_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_typecheck_gate_ignores_invalid_yaml(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "invalid.yml").write_text(
        "invalid: [yaml",
        encoding="utf-8",
    )

    result = check_typecheck_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_typecheck_gate_fails_when_jobs_are_invalid(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  typecheck: invalid
""",
        encoding="utf-8",
    )

    result = check_typecheck_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_typecheck_gate_fails_when_steps_are_invalid(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  typecheck:
    steps: invalid
""",
        encoding="utf-8",
    )

    result = check_typecheck_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_typecheck_gate_ignores_invalid_steps(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  typecheck:
    steps:
      - invalid-step
      - run: echo "not a typecheck"
""",
        encoding="utf-8",
    )

    result = check_typecheck_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_typecheck_gate_ignores_non_string_run(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  typecheck:
    steps:
      - run: 123
""",
        encoding="utf-8",
    )

    result = check_typecheck_gate(tmp_path)

    assert result.status == CheckStatus.FAIL
