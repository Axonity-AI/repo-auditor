"""Tests for RepositoryAuditor."""

from pathlib import Path

from repo_auditor.auditor import RepositoryAuditor
from repo_auditor.models import CheckStatus


def test_auditor_runs_codeowners_check(tmp_path: Path) -> None:
    """Auditor runs the CODEOWNERS check."""

    (tmp_path / "CODEOWNERS").write_text("* @axonity-ai", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("Proprietary license", encoding="utf-8")
    (tmp_path / "SECURITY.md").write_text("# Security", encoding="utf-8")

    auditor = RepositoryAuditor(tmp_path)

    results = auditor.audit()

    assert len(results) == 3
    assert results[0].name == "CODEOWNERS"
    assert results[0].status == CheckStatus.PASS
    assert results[1].name == "LICENSE"
    assert results[1].status == CheckStatus.PASS
    assert results[2].name == "SECURITY"
    assert results[2].status == CheckStatus.PASS


def test_auditor_detects_failed_check(tmp_path: Path) -> None:
    """Auditor reports failed checks."""

    auditor = RepositoryAuditor(tmp_path)

    results = auditor.audit()

    assert auditor.get_exit_code(results) == 1


def test_auditor_returns_zero_when_all_checks_pass(
    tmp_path: Path,
) -> None:
    """Auditor returns zero when all checks pass."""

    (tmp_path / "CODEOWNERS").write_text(
        "* @axonity-ai",
        encoding="utf-8",
    )
    (tmp_path / "LICENSE").write_text(
        "Proprietary license",
        encoding="utf-8",
    )
    (tmp_path / "SECURITY.md").write_text(
        "# Security",
        encoding="utf-8",
    )

    auditor = RepositoryAuditor(tmp_path)

    results = auditor.audit()

    assert auditor.get_exit_code(results) == 0
