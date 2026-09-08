from pathlib import Path

from repo_auditor.checks.test_gate import check_test_gate
from repo_auditor.models import CheckStatus


def test_test_gate_passes_with_test_script(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
jobs:
  verification:
    steps:
      - run: ./scripts/test.sh
""",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.PASS


def test_test_gate_passes_when_test_runs_after_other_command(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
jobs:
  verification:
    steps:
      - run: npm install && npm test
""",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.PASS


def test_test_gate_fails_when_only_build_runs(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
jobs:
  build:
    steps:
      - run: npm run build
""",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_test_gate_fails_when_test_only_appears_in_job_name(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
jobs:
  test:
    steps:
      - run: npm run build
""",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_test_gate_fails_when_testing_tool_is_only_installed(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
jobs:
  setup:
    steps:
      - run: pip install pytest
""",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_test_gate_fails_when_echo_mentions_test(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
jobs:
  build:
    steps:
      - run: echo "running test later"
""",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_test_gate_fails_when_workflows_directory_is_missing(
    tmp_path: Path,
) -> None:
    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_test_gate_ignores_non_yaml_workflow_file(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "README.md").write_text(
        "pytest",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_test_gate_ignores_yaml_that_is_not_a_dict(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        "- item1\n- item2",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_test_gate_ignores_invalid_jobs_structure(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  - test
""",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_test_gate_ignores_invalid_job_structure(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  test: "invalid job"
""",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_test_gate_ignores_invalid_steps_structure(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  test:
    steps: "invalid steps"
""",
        encoding="utf-8",
    )

    result = check_test_gate(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_test_gate_ignores_non_dict_step(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  test:
    steps:
      - "invalid step"
      - run: echo "not testing"
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
