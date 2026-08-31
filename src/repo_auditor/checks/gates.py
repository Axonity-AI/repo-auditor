"""
CI gate enforcement check.

This module inspects GitHub Actions workflow files and verifies that
important quality and security commands are configured as blocking gates.

A gate is considered protected when a workflow runs one of the supported
commands without allowing the job or individual gate step to continue
after a failure.

The check currently recognizes:
- gitleaks for secret scanning
- ruff for linting
- mypy and tsc for type checking
- pytest and npm test commands for testing

The check fails when a recognized gate uses `continue-on-error: true`,
because this allows the workflow to succeed even when the gate fails.

Invalid or unrelated workflow files are ignored so that other valid
workflow files can still be inspected.
"""

from pathlib import Path

import yaml

from repo_auditor.models import CheckResult, CheckStatus

_GATE_COMMANDS = (
    "gitleaks",
    "ruff",
    "mypy",
    "tsc",
    "pytest",
    "npm test",
    "npm run test",
)


def check_gates(repo_path: Path) -> CheckResult:
    workflows_dir = repo_path / ".github" / "workflows"

    if not workflows_dir.is_dir():
        return CheckResult(
            name="gates",
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

            job_text = str(job)

            contains_gate = any(command in job_text for command in _GATE_COMMANDS)

            if not contains_gate:
                continue

            if job.get("continue-on-error") is True:
                return CheckResult(
                    name="gates",
                    status=CheckStatus.FAIL,
                    message=f"Job '{job_name}' uses continue-on-error.",
                )

            steps = job.get("steps", [])
            if not isinstance(steps, list):
                continue

            for step in steps:
                if not isinstance(step, dict):
                    continue

                if step.get("continue-on-error") is True:
                    run = step.get("run", "")
                    if isinstance(run, str) and any(command in run for command in _GATE_COMMANDS):
                        return CheckResult(
                            name="gates",
                            status=CheckStatus.FAIL,
                            message=(f"Gate step in job '{job_name}' uses continue-on-error."),
                        )

    return CheckResult(
        name="gates",
        status=CheckStatus.PASS,
        message="CI gate checks are configured to block failures.",
    )
