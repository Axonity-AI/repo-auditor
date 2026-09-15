"""
CI secret-scanning gate check.

This module inspects GitHub Actions workflow files and verifies that the
repository's CI configuration includes gitleaks for detecting exposed
secrets.

A repository passes when any valid workflow contains a step that runs
gitleaks.

The check only examines YAML workflow files under `.github/workflows`.
Invalid YAML, unrelated files, malformed workflow structures, and steps
without executable commands are ignored.

The check fails when the workflows directory is missing or when no valid
workflow contains a gitleaks command.
"""

from pathlib import Path

import yaml

from repo_auditor.models import CheckResult, CheckStatus


def check_secret_scanning(repo_path: Path) -> CheckResult:
    workflows_dir = repo_path / ".github" / "workflows"

    if not workflows_dir.is_dir():
        return CheckResult(
            name="secret-scanning",
            status=CheckStatus.FAIL,
            message="GitHub Actions workflows directory is missing.",
        )

    for workflow in workflows_dir.iterdir():
        if workflow.suffix not in {".yml", ".yaml"}:
            continue

        try:
            data = yaml.safe_load(workflow.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue

        if not isinstance(data, dict):
            continue

        jobs = data.get("jobs", {})
        if not isinstance(jobs, dict):
            continue

        for job in jobs.values():
            if not isinstance(job, dict):
                continue

            steps = job.get("steps", [])
            if not isinstance(steps, list):
                continue

            for step in steps:
                if not isinstance(step, dict):
                    continue

                run = step.get("run", "")
                if isinstance(run, str) and "gitleaks" in run:
                    return CheckResult(
                        name="secret-scanning",
                        status=CheckStatus.PASS,
                        message="CI includes gitleaks secret scanning.",
                    )

    return CheckResult(
        name="secret-scanning",
        status=CheckStatus.FAIL,
        message="No CI workflow runs gitleaks.",
    )
