"""Dependabot repository check

Dependabot configuration check.

This module verifies that Dependabot is configured to maintain the
repository's dependencies.

The configuration is read from `.github/dependabot.yml`.

The check verifies that the configuration contains dependency update
entries and that each required update configuration specifies a package
ecosystem.

Invalid YAML, missing configuration, missing updates, or missing package
ecosystem information cause the check to fail.

The check passes when a valid Dependabot configuration contains at least
one dependency update configuration with a package ecosystem.
"""

from pathlib import Path

import yaml

from repo_auditor.models import CheckResult, CheckStatus


def check_dependabot(repo_path: Path) -> CheckResult:
    """Check that Dependabot is configured."""

    config_path = repo_path / ".github" / "dependabot.yml"

    if not config_path.is_file():
        return CheckResult(
            name="DEPENDABOT",
            status=CheckStatus.FAIL,
            message="Missing .github/dependabot.yml.",
        )

    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return CheckResult(
            name="DEPENDABOT",
            status=CheckStatus.FAIL,
            message="Invalid .github/dependabot.yml.",
        )

    if not isinstance(config, dict):
        return CheckResult(
            name="DEPENDABOT",
            status=CheckStatus.FAIL,
            message="Invalid Dependabot configuration.",
        )

    updates = config.get("updates")

    if not isinstance(updates, list) or not updates:
        return CheckResult(
            name="DEPENDABOT",
            status=CheckStatus.FAIL,
            message="No Dependabot updates configured.",
        )

    for update in updates:
        if isinstance(update, dict) and update.get("package-ecosystem"):
            return CheckResult(
                name="DEPENDABOT",
                status=CheckStatus.PASS,
                message="Dependabot is configured.",
            )

    return CheckResult(
        name="DEPENDABOT",
        status=CheckStatus.FAIL,
        message="No package ecosystem configured for Dependabot.",
    )
