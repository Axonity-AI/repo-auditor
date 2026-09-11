# Repo Auditor
version = "1.5.0"

## Overview
Repo Auditor is a command-line tool/interface that analyzes software repositories against the engineering, security, and development standards defined by Axonity. It exists to automate repository audits, identify missing or non-compliant configurations, and provide clear feedback that helps maintain consistent and reliable engineering practices across projects.

This repository complements the existing Git/CI checks rather than replacing them. The checks follow the same Axonity engineering standards, but while the CI checks run as part of the pull request workflow, Repo Auditor can be run directly from the CLI at any time. This makes it faster and easier for developers to validate their repositories locally without needing to push changes and open a pull request first, while also making it easier to add and maintain additional checks as Axonity’s standards evolve. The CI checks are still needed as a final automated safeguard to ensure standards are enforced before changes are merged.


## Checks

Repo Auditor currently checks for:

- ADR documentation
- GitHub Actions CI workflows
- CODEOWNERS
- Conventional Commits configuration
- Dependabot configuration
- License file
- Pre-commit configuration
- Security policy
- Secret scanning with gitleaks
- CI failure gates
- Ruff linting gate
- Test execution gate
- Type-checking gate


## Project Structure

    src/repo_auditor/
    ├── checks/          # Individual repository compliance checks
    ├── auditor.py       # Audit orchestration
    ├── cli.py           # Command-line interface
    ├── models.py        # Shared audit result models
    └── output.py        # Human-readable and JSON output

    tests/
    ├── checks/          # Tests for individual checks
    └── test_*.py        # Auditor, CLI, and output tests


## Logged Changes

Development and implementation changes are documented in:

- `docs/ADR.md` for crucial decisions made during implementation.
- `CHANGELOG.md` for changes grouped by release.

## Quickstart (dev)

Set up the development environment:

    python scripts/manage.py --setup

Run the test suite:

    python scripts/manage.py --test

### Global CLI Installation

First, install pipx as its a dependency

    pip install pipx

To install Repo Auditor as a globally available CLI:

    python scripts/manage.py --install

Once installed, you can use it from any directory:

    repo-auditor <repository-path>

### Version Management

Update the version using:

    python scripts/bump_version.py --patch

    python scripts/bump_version.py --minor

    python scripts/bump_version.py --major

Or set a specific version:

    python scripts/bump_version.py --set 2.0.0

## Deploy notes
```bash
docker build -t repo_auditor -f docker/Dockerfile .
docker compose -f docker/compose.yml up
```

## New to the team?
Read [ONBOARDING.md](ONBOARDING.md) first — the day-to-day workflow (branches, PRs,
CI, commit format, ADRs), written assuming no prior experience with any of it.
[ENGINEERING_STANDARDS.md](ENGINEERING_STANDARDS.md) covers why we work this way.

## Contacts
Owner: Axonity AI
Authors: prchS
