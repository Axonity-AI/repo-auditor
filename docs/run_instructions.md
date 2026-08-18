# Run Instructions

## Local dev
```bash
./scripts/run_local.sh
```

## Docker
```bash
docker build -t {{PACKAGE_NAME}} -f docker/Dockerfile .
docker compose -f docker/compose.yml up
```

## Environment variables
Copy `.env.example` to `.env` and fill in values before running.
