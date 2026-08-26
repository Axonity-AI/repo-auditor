"""Repository audit orchestration."""

from pathlib import Path

from repo_auditor.checks.codeowners import check_codeowners
from repo_auditor.checks.license import check_license
from repo_auditor.checks.security import check_security
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
        ]

    @staticmethod
    def get_exit_code(results: list[CheckResult]) -> int:
        """Return 1 when a check fails, otherwise 0."""

        if any(result.status == CheckStatus.FAIL for result in results):
            return 1

        return 0
