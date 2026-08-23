"""Audit result formatting."""

import json

from repo_auditor.models import CheckResult


def format_human(results: list[CheckResult]) -> str:
    """Format audit results for terminal output."""

    lines = [
        "",
        "AXONITY REPOSITORY AUDIT",
        "=" * 30,
    ]

    for result in results:
        lines.append(f"[{result.status.value.upper()}] " f"{result.name}: {result.message}")

        if result.details:
            lines.append(f"  Details: {result.details}")

    passed = sum(result.status.value == "pass" for result in results)
    failed = sum(result.status.value == "fail" for result in results)
    warnings = sum(result.status.value == "warning" for result in results)

    lines.extend(
        [
            "",
            "-" * 30,
            f"Passed: {passed}",
            f"Failed: {failed}",
            f"Warnings: {warnings}",
            "",
        ]
    )

    return "\n".join(lines)


def format_json(results: list[CheckResult]) -> str:
    """Format audit results as JSON."""

    data = [
        {
            "name": result.name,
            "status": result.status.value,
            "message": result.message,
            "details": result.details,
        }
        for result in results
    ]

    return json.dumps(data, indent=2)
