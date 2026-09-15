"""CI repository check

Continuous Integration (CI) workflow check.

This module verifies that the repository contains at least one valid
GitHub Actions workflow with a configured job.

Workflow files are read from `.github/workflows` and only YAML workflow
files are inspected.

Invalid YAML and workflows without jobs are ignored so that other valid
workflow files can still be evaluated.

The check passes when at least one valid workflow contains a job.
It fails when the workflows directory is missing or no valid workflow
contains a job.
"""

from pathlib import Path

import yaml

from repo_auditor.models import CheckResult, CheckStatus


def check_ci_exists(repo_path: Path) -> CheckResult:
    """Check that the repository contains a valid CI workflow."""

    workflows_dir = repo_path / ".github" / "workflows"

    if not workflows_dir.is_dir():
        return CheckResult(
            name="CI",
            status=CheckStatus.FAIL,
            message="Missing .github/workflows directory.",
        )

    workflow_files = [
        *workflows_dir.glob("*.yml"),
        *workflows_dir.glob("*.yaml"),
    ]

    if not workflow_files:
        return CheckResult(
            name="CI",
            status=CheckStatus.FAIL,
            message="No CI workflow files found.",
        )

    for workflow_file in workflow_files:
        try:
            config = yaml.safe_load(workflow_file.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue

        if isinstance(config, dict) and config.get("jobs"):
            return CheckResult(
                name="CI",
                status=CheckStatus.PASS,
                message=f"CI workflow found: {workflow_file.name}.",
            )

    return CheckResult(
        name="CI",
        status=CheckStatus.FAIL,
        message="No valid CI workflow with jobs found.",
    )
