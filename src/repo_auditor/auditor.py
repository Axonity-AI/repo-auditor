"""Repository audit framework.


This module coordinates all repository compliance checks and combines
their results into a single audit.

Each individual check is responsible for evaluating one repository
requirement and returning a CheckResult. RepositoryAuditor runs the
registered checks in a consistent order and collects their results.

The auditor also determines the process exit code from the collected
results. A zero exit code indicates that all checks passed, while a
non-zero exit code indicates that at least one check failed.

This module provides the central integration point between the individual
checks and the CLI.
"""

from pathlib import Path

from repo_auditor.checks.adrs import check_adrs
from repo_auditor.checks.ci_exists import check_ci_exists
from repo_auditor.checks.codeowners import check_codeowners
from repo_auditor.checks.conventional_commits import check_conventional_commits
from repo_auditor.checks.dependabot import check_dependabot
from repo_auditor.checks.gates import check_gates
from repo_auditor.checks.license import check_license
from repo_auditor.checks.lint_gate import check_lint_gate
from repo_auditor.checks.pre_commit import check_pre_commit
from repo_auditor.checks.secret_scanning import check_secret_scanning
from repo_auditor.checks.security import check_security
from repo_auditor.checks.test_gate import check_test_gate
from repo_auditor.checks.typecheck_gate import check_typecheck_gate
from repo_auditor.models import CheckResult, CheckStatus


class RepositoryAuditor:
    """Run repository audit checks."""

    def __init__(self, repo_path: Path) -> None:
        """Initialize the auditor."""

        self.repo_path = repo_path.resolve()

    def audit(self) -> list[CheckResult]:
        """Run all registered checks."""

        return [
            check_codeowners(self.repo_path),
            check_license(self.repo_path),
            check_security(self.repo_path),
            check_dependabot(self.repo_path),
            check_ci_exists(self.repo_path),
            check_pre_commit(self.repo_path),
            check_conventional_commits(self.repo_path),
            check_adrs(self.repo_path),
            check_secret_scanning(self.repo_path),
            check_gates(self.repo_path),
            check_lint_gate(self.repo_path),
            check_typecheck_gate(self.repo_path),
            check_test_gate(self.repo_path),
        ]

    @staticmethod
    def get_exit_code(results: list[CheckResult]) -> int:
        """Return 1 when a check fails, otherwise 0."""

        if any(result.status == CheckStatus.FAIL for result in results):
            return 1

        return 0
