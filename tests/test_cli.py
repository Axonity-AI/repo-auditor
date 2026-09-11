"""Tests for the CLI."""

import json
from pathlib import Path

from click.testing import CliRunner

from repo_auditor.cli import main


def create_valid_repository(repo_path: Path) -> None:
    """Create a repository that passes all audit checks."""

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

    github_dir = repo_path / ".github"
    workflows_dir = github_dir / "workflows"
    workflows_dir.mkdir(parents=True)

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

    (workflows_dir / "ci.yml").write_text(
        """
name: CI

on:
  push:
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ruff check .

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - run: mypy src

  test:
    runs-on: ubuntu-latest
    steps:
      - run: pytest

  security:
    runs-on: ubuntu-latest
    steps:
      - run: gitleaks detect --no-banner
""",
        encoding="utf-8",
    )

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

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        files: ^src/
""",
        encoding="utf-8",
    )

    adr_dir = repo_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)

    (adr_dir / "0001-example.md").write_text(
        "# ADR 0001: Example",
        encoding="utf-8",
    )


def test_cli_passes_when_repository_passes(
    tmp_path: Path,
) -> None:
    """CLI exits zero when all checks pass."""

    create_valid_repository(tmp_path)

    runner = CliRunner()

    result = runner.invoke(main, [str(tmp_path)])

    assert result.exit_code == 0
    assert "[PASS] CODEOWNERS" in result.output
    assert "[PASS] LICENSE" in result.output
    assert "[PASS] SECURITY" in result.output


def test_cli_fails_when_check_fails(
    tmp_path: Path,
) -> None:
    """CLI exits one when a check fails."""

    runner = CliRunner()

    result = runner.invoke(main, [str(tmp_path)])

    assert result.exit_code == 1
    assert "[FAIL] CODEOWNERS" in result.output


def test_cli_supports_json_output(
    tmp_path: Path,
) -> None:
    """CLI supports JSON output."""

    create_valid_repository(tmp_path)

    runner = CliRunner()

    result = runner.invoke(
        main,
        [str(tmp_path), "--json"],
    )

    assert result.exit_code == 0

    data = json.loads(result.output)

    assert len(data) == 13

    assert data[0]["name"] == "CODEOWNERS"
    assert data[0]["status"] == "pass"
    assert data[1]["name"] == "LICENSE"
    assert data[1]["status"] == "pass"
    assert data[2]["name"] == "SECURITY"
    assert data[2]["status"] == "pass"

    assert all(item["status"] == "pass" for item in data)
