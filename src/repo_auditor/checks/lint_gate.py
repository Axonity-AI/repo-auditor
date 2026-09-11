"""
CI lint gate check.

This module inspects GitHub Actions workflow files and verifies that the
repository's CI configuration includes a linting process.

The check only examines YAML workflow files under `.github/workflows`.
Invalid YAML, unrelated files, malformed workflow structures, and steps
that do not contain executable commands are ignored.

The check fails when the workflows directory is missing or when no valid
workflow contains a linting command.
"""

from pathlib import Path

import yaml

from repo_auditor.checks._process_gate import has_process_command
from repo_auditor.models import CheckResult, CheckStatus


def check_lint_gate(repo_path: Path) -> CheckResult:
    workflows_dir = repo_path / ".github" / "workflows"

    if not workflows_dir.is_dir():
        return CheckResult(
            name="lint-gate",
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

        for job_name, job in jobs.items():
            if not isinstance(job, dict):
                continue

            steps = job.get("steps", [])
            if not isinstance(steps, list):
                continue

            for step in steps:
                if not isinstance(step, dict):
                    continue

                run = step.get("run")
                step_name = step.get("name", "")
                if isinstance(run, str) and has_process_command(
                    run,
                    "lint",
                    job_name=str(job_name),
                    step_name=step_name if isinstance(step_name, str) else "",
                ):
                    return CheckResult(
                        name="lint-gate",
                        status=CheckStatus.PASS,
                        message="CI includes a linting gate.",
                    )

    return CheckResult(
        name="lint-gate",
        status=CheckStatus.FAIL,
        message="No CI workflow performs linting.",
    )
