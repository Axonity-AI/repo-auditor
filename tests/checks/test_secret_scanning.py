from pathlib import Path

from repo_auditor.checks.secret_scanning import check_secret_scanning
from repo_auditor.models import CheckStatus


def test_secret_scanning_ignores_non_workflow_files(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "README.md").write_text(
        "gitleaks",
        encoding="utf-8",
    )

    result = check_secret_scanning(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_secret_scanning_ignores_invalid_yaml(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "invalid.yml").write_text(
        "invalid: [yaml",
        encoding="utf-8",
    )

    result = check_secret_scanning(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_secret_scanning_fails_when_no_jobs_exist(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI
""",
        encoding="utf-8",
    )

    result = check_secret_scanning(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_secret_scanning_fails_when_jobs_are_invalid(
    tmp_path: Path,
) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  security: invalid
""",
        encoding="utf-8",
    )

    result = check_secret_scanning(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_secret_scanning_fails_when_steps_are_invalid(
    tmp_path: Path,
) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  security:
    steps: invalid
""",
        encoding="utf-8",
    )

    result = check_secret_scanning(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_secret_scanning_ignores_invalid_steps(
    tmp_path: Path,
) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  security:
    steps:
      - invalid-step
      - run: echo "nothing here"
""",
        encoding="utf-8",
    )

    result = check_secret_scanning(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_secret_scanning_ignores_non_string_run(
    tmp_path: Path,
) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)

    (workflows / "ci.yml").write_text(
        """
name: CI

jobs:
  security:
    steps:
      - run: 123
""",
        encoding="utf-8",
    )

    result = check_secret_scanning(tmp_path)

    assert result.status == CheckStatus.FAIL
