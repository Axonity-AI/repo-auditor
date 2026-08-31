from pathlib import Path

from repo_auditor.checks.test_gate import check_test_gate
from repo_auditor.models import CheckStatus


def test_test_gate_passes_with_npm_test(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  test:
    steps:
      - run: npm test
""",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.PASS


def test_test_gate_passes_with_npm_run_test(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  test:
    steps:
      - run: npm run test
""",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.PASS


def test_test_gate_ignores_non_workflow_files(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "README.md").write_text(
        "pytest",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_test_gate_ignores_invalid_yaml(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "invalid.yml").write_text(
        "invalid: [yaml",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_test_gate_fails_when_jobs_are_invalid(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  test: invalid
""",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_test_gate_fails_when_steps_are_invalid(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  test:
    steps: invalid
""",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_test_gate_ignores_invalid_steps(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  test:
    steps:
      - invalid-step
      - run: echo "not a test"
""",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_test_gate_ignores_non_string_run(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  test:
    steps:
      - run: 123
""",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL
