
# ADR 0001: Streamlining of the script installation and testing

**Status:** Proposed

**Date:** 2026-08-28

## Context

Repo Auditor needs to support two use cases: developers working on the project and users who only want to install and use the Repo Auditor CLI to audit other repositories.

The development workflow requires a project-local virtual environment, development dependencies, editable installation, and pre-commit hooks. CLI users need Repo Auditor and its runtime dependencies to be isolated from the system Python environment while still being available as a globally accessible command.

The project should also work across Windows, Linux, macOS, WSL, Bash, and PowerShell without maintaining separate workflow logic for each shell.

## Decision

Use a single cross-platform Python management script with flags for development setup, global CLI installation, and testing.

The development workflow will create and use a project-local `.venv`. Global CLI installation will create a separate dedicated virtual environment and add its executable directory to the user's `PATH`.

## Alternatives considered

- **Separate Bash and PowerShell scripts** — Rejected because this duplicates workflow logic and requires users to choose the correct script for their shell.

- **Install all dependencies globally** — Rejected because it can pollute the system Python environment and cause dependency conflicts.

- **Use pipx** — Rejected because a dedicated virtual environment provides dependency isolation and global CLI access without requiring an additional package manager.

- **Use the development virtual environment for global CLI usage** — Rejected because users who only want to audit repositories should not need the full development environment.

## Consequences

Developers have a single cross-platform command for setting up and testing Repo Auditor.

CLI users can install Repo Auditor into a dedicated virtual environment and use the `repo-auditor` command from any directory without modifying the system Python environment.

The management script must maintain the user's `PATH` configuration, and users may need to restart their terminal after installation.

The project now maintains two separate virtual environments when both workflows are used: one for development and one for the globally available CLI.




# ADR 0000: <short title of the decision>

**Status:** Proposed | Accepted | Superseded by ADR-XXXX | Deprecated
**Date:** YYYY-MM-DD

## Context

What problem forced this decision? What constraints (technical, cost, timeline, team size) shaped it? A future reader should understand the situation without needing to have been in the room.

## Decision

What was decided, stated plainly in one or two sentences.

## Alternatives considered

- **Option A** — why it was rejected.
- **Option B** — why it was rejected.

## Consequences

What becomes easier or harder as a result. Include the real trade-offs, not just the upside — an ADR that only lists benefits isn't trustworthy the next time someone reads it while debugging a problem this decision caused.

---

*One ADR per significant, hard-to-reverse technical decision (choice of database, auth strategy, major dependency, architectural pattern) — not for routine implementation details that a code review already covers. Number sequentially (0001, 0002, ...), never reuse or renumber. To reverse a decision, write a new ADR and mark the old one "Superseded by ADR-XXXX" rather than editing it — the history of *why* something changed is the point.*
