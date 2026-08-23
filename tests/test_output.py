"""Tests for audit output."""

import json

from repo_auditor.models import CheckResult, CheckStatus
from repo_auditor.output import format_human, format_json


def test_format_human() -> None:
    """Human output contains audit results."""

    results = [
        CheckResult(
            name="CODEOWNERS",
            status=CheckStatus.PASS,
            message="CODEOWNERS file exists and is non-empty.",
        )
    ]

    output = format_human(results)

    assert "[PASS] CODEOWNERS" in output
    assert "Passed: 1" in output
    assert "Failed: 0" in output


def test_format_json() -> None:
    """JSON output contains structured results."""

    results = [
        CheckResult(
            name="CODEOWNERS",
            status=CheckStatus.FAIL,
            message="CODEOWNERS file does not exist.",
        )
    ]

    output = format_json(results)
    data = json.loads(output)

    assert data[0]["name"] == "CODEOWNERS"
    assert data[0]["status"] == "fail"
    assert data[0]["message"] == "CODEOWNERS file does not exist."
