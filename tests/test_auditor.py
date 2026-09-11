"""Tests for RepositoryAuditor."""

from pathlib import Path

from repo_auditor.auditor import RepositoryAuditor
from repo_auditor.models import CheckStatus


def create_valid_repository(repo_path: Path) -> None:
    """Create a repository that passes all audit checks."""

    # Required repository files.
    (repo_path / "CODEOWNERS").write_text(
        "* @axonity-ai",
        encoding="utf-8",
    )
    (repo_path / "LICENSE").write_text(
        "Proprietary license",
        encoding="utf-8",
    )
    (repo_path / "SECURITY.md").write_text(
        "# Security",
        encoding="utf-8",
    )

    # GitHub configuration directories.
    github_dir = repo_path / ".github"
    workflows_dir = github_dir / "workflows"
    workflows_dir.mkdir(parents=True)

    # Dependabot configuration.
    (github_dir / "dependabot.yml").write_text(
        """
version: 2
updates:
  - package-ecosystem: pip
    directory: /
    schedule:
      interval: weekly
""",
        encoding="utf-8",
    )

    # CI workflow containing the required test job.
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

    # Lint gate.
    (workflows_dir / "lint.yml").write_text(
        """
name: Lint

on:
  push:
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ruff check .
""",
        encoding="utf-8",
    )

    # Type-check gate.
    (workflows_dir / "typecheck.yml").write_text(
        """
name: Typecheck

on:
  push:
  pull_request:

jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - run: mypy src
""",
        encoding="utf-8",
    )

    # Test gate.
    (workflows_dir / "test.yml").write_text(
        """
name: Tests

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

    # Secret-scanning gate.
    (workflows_dir / "security.yml").write_text(
        """
name: Security

on:
  push:
  pull_request:

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - run: gitleaks detect --source .
""",
        encoding="utf-8",
    )

    # Pre-commit configuration.
    (repo_path / ".pre-commit-config.yaml").write_text(
        """
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.24.2
    hooks:
      - id: gitleaks

  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v4.2.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
""",
        encoding="utf-8",
    )

    # ADR.
    adr_dir = repo_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)

    (adr_dir / "0001-example.md").write_text(
        "# ADR 0001: Example",
        encoding="utf-8",
    )


def test_auditor_runs_all_checks(tmp_path: Path) -> None:
    """Auditor runs all registered checks."""

    create_valid_repository(tmp_path)

    auditor = RepositoryAuditor(tmp_path)

    results = auditor.audit()

    assert len(results) == 13
    assert all(result.status == CheckStatus.PASS for result in results)


def test_auditor_detects_failed_check(tmp_path: Path) -> None:
    """Auditor reports failed checks."""

    auditor = RepositoryAuditor(tmp_path)

    results = auditor.audit()

    assert auditor.get_exit_code(results) == 1


def test_auditor_returns_zero_when_all_checks_pass(
    tmp_path: Path,
) -> None:
    """Auditor returns zero when all checks pass."""

    create_valid_repository(tmp_path)

    auditor = RepositoryAuditor(tmp_path)

    results = auditor.audit()

    assert auditor.get_exit_code(results) == 0
