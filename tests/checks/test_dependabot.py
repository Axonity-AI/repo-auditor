"""Tests for the Dependabot check."""

from pathlib import Path

from repo_auditor.checks.dependabot import check_dependabot
from repo_auditor.models import CheckStatus


def test_dependabot_passes(tmp_path: Path) -> None:
    """Dependabot check passes with valid configuration."""

    github_dir = tmp_path / ".github"
    github_dir.mkdir()

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

    result = check_dependabot(tmp_path)

    assert result.status == CheckStatus.PASS


def test_dependabot_fails_when_missing(tmp_path: Path) -> None:
    """Dependabot check fails when configuration is missing."""

    result = check_dependabot(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_dependabot_fails_without_updates(tmp_path: Path) -> None:
    """Dependabot check fails without update configuration."""

    github_dir = tmp_path / ".github"
    github_dir.mkdir()

    (github_dir / "dependabot.yml").write_text(
        """
version: 2
""",
        encoding="utf-8",
    )

    result = check_dependabot(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_dependabot_fails_without_ecosystem(tmp_path: Path) -> None:
    """Dependabot check fails without a package ecosystem."""

    github_dir = tmp_path / ".github"
    github_dir.mkdir()

    (github_dir / "dependabot.yml").write_text(
        """
version: 2
updates:
  - directory: /
    schedule:
      interval: weekly
""",
        encoding="utf-8",
    )

    result = check_dependabot(tmp_path)

    assert result.status == CheckStatus.FAIL


def test_dependabot_fails_with_invalid_yaml(tmp_path: Path) -> None:
    """Dependabot check fails when YAML is invalid."""

    github_dir = tmp_path / ".github"
    github_dir.mkdir()

    (github_dir / "dependabot.yml").write_text(
        """
version: [
this is invalid yaml
""",
        encoding="utf-8",
    )

    result = check_dependabot(tmp_path)

    assert result.status == CheckStatus.FAIL
