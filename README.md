# Repo Auditor

## Overview
Repo Auditor is a command-line tool/interface that analyzes software repositories against the engineering, security, and development standards defined by Axonity. It exists to automate repository audits, identify missing or non-compliant configurations, and provide clear feedback that helps maintain consistent and reliable engineering practices across projects.

## Quickstart (dev)
```bash
./scripts/setup.sh    # one-time: installs deps + activates pre-commit hooks
./scripts/run_local.sh
```
`run_local.sh` creates a virtualenv, installs dependencies, loads `.env`/`.env.example`, and starts the app.

## Run tests
```bash
pytest -q
```

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
