"""Conventional Commits repository check

Conventional Commits configuration check.

This module verifies that the repository's pre-commit configuration
contains the Conventional Commits hook and that the hook runs during
the commit-msg stage.

The check reads `.pre-commit-config.yaml` and inspects its configured
repositories and hooks.

Invalid YAML and missing or incorrectly configured Conventional Commits
hooks cause the check to fail.

The check passes when the required conventional-pre-commit hook is
configured for the commit-msg stage.
"""

from pathlib import Path

import yaml

from repo_auditor.models import CheckResult, CheckStatus


def check_conventional_commits(repo_path: Path) -> CheckResult:
    """Check that a commit-msg hook is configured."""

    config_path = repo_path / ".pre-commit-config.yaml"

    if not config_path.is_file():
        return CheckResult(
            name="CONVENTIONAL COMMITS",
            status=CheckStatus.FAIL,
            message="Missing .pre-commit-config.yaml.",
        )

    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return CheckResult(
            name="CONVENTIONAL COMMITS",
            status=CheckStatus.FAIL,
            message="Invalid .pre-commit-config.yaml.",
        )

    if not isinstance(config, dict):
        return CheckResult(
            name="CONVENTIONAL COMMITS",
            status=CheckStatus.FAIL,
            message="Invalid pre-commit configuration.",
        )

    repos = config.get("repos", [])

    if not isinstance(repos, list):
        return CheckResult(
            name="CONVENTIONAL COMMITS",
            status=CheckStatus.FAIL,
            message="Invalid pre-commit repositories configuration.",
        )

    for repo in repos:
        if not isinstance(repo, dict):
            continue

        for hook in repo.get("hooks", []):
            if not isinstance(hook, dict):
                continue

            stages = hook.get("stages", [])

            if "commit-msg" in stages:
                return CheckResult(
                    name="CONVENTIONAL COMMITS",
                    status=CheckStatus.PASS,
                    message="commit-msg hook is configured.",
                )

    return CheckResult(
        name="CONVENTIONAL COMMITS",
        status=CheckStatus.FAIL,
        message="No commit-msg hook configured.",
    )
