"""
CI test gate check.

This module inspects GitHub Actions workflow files and verifies that the
repository's CI configuration runs an automated test command.

The check supports common test commands for Python and Node.js projects:
- pytest
- npm test
- npm run test

A repository passes when any valid workflow contains a step running one
of these supported commands.

The check only examines YAML workflow files under `.github/workflows`.
Invalid YAML, unrelated files, malformed workflow structures, and steps
without executable commands are ignored.

The check fails when the workflows directory is missing or when no valid
workflow contains a supported test command.
"""

from pathlib import Path

import yaml

from repo_auditor.models import CheckResult, CheckStatus


def check_test_gate(repo_path: Path) -> CheckResult:
    workflows_dir = repo_path / ".github" / "workflows"

    if not workflows_dir.is_dir():
        return CheckResult(
            name="test-gate",
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
                if isinstance(run, str) and ("pytest" in run or "npm test" in run or "npm run test" in run):
                    return CheckResult(
                        name="test-gate",
                        status=CheckStatus.PASS,
                        message="CI includes a test gate.",
                    )

    return CheckResult(
        name="test-gate",
        status=CheckStatus.FAIL,
        message="No CI workflow runs a supported test command.",
    )
