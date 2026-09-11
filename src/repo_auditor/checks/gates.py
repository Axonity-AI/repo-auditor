"""
CI gate enforcement check.

This module inspects GitHub Actions workflow files and verifies that
important quality and security commands are configured as blocking gates.

A gate is considered protected when a workflow runs one of the supported
processes without allowing the job or individual gate step to continue
after a failure.

The check fails when a recognized gate uses `continue-on-error: true`,
because this allows the workflow to succeed even when the gate fails.

Invalid or unrelated workflow files are ignored so that other valid
workflow files can still be inspected.
"""

from pathlib import Path

import yaml

from repo_auditor.checks._process_gate import has_process_command
from repo_auditor.models import CheckResult, CheckStatus


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

            steps = job.get("steps", [])
            if not isinstance(steps, list):
                continue

            gate_steps = [
                step
                for step in steps
                if (
                    isinstance(step, dict)
                    and isinstance(step.get("run"), str)
                    and any(
                        has_process_command(
                            step["run"],
                            gate_type,
                            job_name=str(job_name),
                            step_name=str(step.get("name") or ""),
                        )
                        for gate_type in (
                            "lint",
                            "typecheck",
                            "test",
                            "security",
                        )
                    )
                )
            ]

            if not gate_steps:
                continue

            if job.get("continue-on-error") is True:
                return CheckResult(
                    name="gates",
                    status=CheckStatus.FAIL,
                    message=f"Job '{job_name}' uses continue-on-error.",
                )

            for step in gate_steps:
                if step.get("continue-on-error") is True:
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
