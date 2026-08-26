"""Tests for the CLI."""

import json
from pathlib import Path

from click.testing import CliRunner

from repo_auditor.cli import main


def test_cli_passes_when_repository_passes(
    tmp_path: Path,
) -> None:
    """CLI exits zero when all checks pass."""

    (tmp_path / "CODEOWNERS").write_text(
        "* @axonity-ai",
        encoding="utf-8",
    )
    (tmp_path / "LICENSE").write_text(
        "Proprietary license",
        encoding="utf-8",
    )
    (tmp_path / "SECURITY.md").write_text(
        "# Security",
        encoding="utf-8",
    )

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

    (tmp_path / "CODEOWNERS").write_text(
        "* @axonity-ai",
        encoding="utf-8",
    )
    (tmp_path / "LICENSE").write_text(
        "Proprietary license",
        encoding="utf-8",
    )
    (tmp_path / "SECURITY.md").write_text(
        "# Security",
        encoding="utf-8",
    )

    runner = CliRunner()

    result = runner.invoke(
        main,
        [str(tmp_path), "--json"],
    )

    assert result.exit_code == 0

    data = json.loads(result.output)

    assert data[0]["name"] == "CODEOWNERS"
    assert data[0]["status"] == "pass"
    assert data[1]["name"] == "LICENSE"
    assert data[1]["status"] == "pass"
    assert data[2]["name"] == "SECURITY"
    assert data[2]["status"] == "pass"
