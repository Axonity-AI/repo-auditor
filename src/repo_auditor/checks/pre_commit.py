"""Check for pre-commit configuration

Pre-commit configuration check.

This module verifies that the repository contains a valid
`.pre-commit-config.yaml` configuration file.

Pre-commit provides automated checks that run before changes are
committed, helping enforce repository standards consistently across
developers and environments.

The check reads the configuration as YAML and verifies that it is a valid
structured configuration.

The check passes when the configuration file exists and contains valid
YAML.

The check fails when the file is missing or contains invalid YAML.
"""

from pathlib import Path

import yaml

from repo_auditor.models import CheckResult, CheckStatus


def check_pre_commit(repo_path: Path) -> CheckResult:
    """Check that a valid pre-commit configuration exists."""

    config_path = repo_path / ".pre-commit-config.yaml"

    if not config_path.is_file():
        return CheckResult(
            name="PRE-COMMIT",
            status=CheckStatus.FAIL,
            message="Pre-commit configuration does not exist.",
        )

    try:
        with config_path.open(encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except yaml.YAMLError:
        return CheckResult(
            name="PRE-COMMIT",
            status=CheckStatus.FAIL,
            message="Pre-commit configuration contains invalid YAML.",
        )

    if not isinstance(config, dict):
        return CheckResult(
            name="PRE-COMMIT",
            status=CheckStatus.FAIL,
            message="Pre-commit configuration is invalid.",
        )

    repos = config.get("repos")

    if not isinstance(repos, list) or not repos:
        return CheckResult(
            name="PRE-COMMIT",
            status=CheckStatus.FAIL,
            message="Pre-commit configuration contains no repositories.",
        )

    return CheckResult(
        name="PRE-COMMIT",
        status=CheckStatus.PASS,
        message="Pre-commit configuration exists and is valid.",
    )
