# {{PROJECT_NAME}}

## Overview
One paragraph: what this project does and why it exists.

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
docker build -t {{PACKAGE_NAME}} -f docker/Dockerfile .
docker compose -f docker/compose.yml up
```

## New to the team?
Read [ONBOARDING.md](ONBOARDING.md) first — the day-to-day workflow (branches, PRs,
CI, commit format, ADRs), written assuming no prior experience with any of it.
[ENGINEERING_STANDARDS.md](ENGINEERING_STANDARDS.md) covers why we work this way.

## Contacts
Owner: TBD
