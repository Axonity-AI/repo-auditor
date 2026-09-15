"""
CI type-check gate check.

This module inspects GitHub Actions workflow files and verifies that the
repository's CI configuration performs static type checking.

The check supports:
- mypy for Python projects
- tsc for TypeScript projects

A repository passes when any valid workflow contains a step running one
of these supported type-checking commands.

The check only examines YAML workflow files under `.github/workflows`.
Invalid YAML, unrelated files, malformed workflow structures, and steps
without executable commands are ignored.

The check fails when the workflows directory is missing or when no valid
workflow contains a supported type-checking command.
"""

from pathlib import Path

import yaml

from repo_auditor.models import CheckResult, CheckStatus


def check_typecheck_gate(repo_path: Path) -> CheckResult:
    workflows_dir = repo_path / ".github" / "workflows"

    if not workflows_dir.is_dir():
        return CheckResult(
            name="typecheck-gate",
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
                if not isinstance(run, str):
                    continue

                if "mypy" in run or "tsc" in run:
                    return CheckResult(
                        name="typecheck-gate",
                        status=CheckStatus.PASS,
                        message="CI includes a type-check gate.",
                    )

    return CheckResult(
        name="typecheck-gate",
        status=CheckStatus.FAIL,
        message="No CI workflow runs mypy or tsc.",
    )
