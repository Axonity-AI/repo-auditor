"""
Audit result output formatting.

This module converts repository audit results into formats suitable for
displaying to users or consuming by other tools.

The human formatter produces readable terminal output containing each
check's status, message, optional details, and a summary of passed,
failed, and warning checks.

The JSON formatter produces structured output containing the same result
information, making it suitable for scripts, CI systems, and other
automated consumers.

Both formatters operate on the shared CheckResult model so that output
formatting remains separate from the audit and check implementations.
"""

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
        lines.append(f"[{result.status.value.upper()}] {result.name}: {result.message}")

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
