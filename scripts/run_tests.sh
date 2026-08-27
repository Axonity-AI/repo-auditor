#!/bin/bash
# test.sh - runs the project's test suite using the active virtual environment
# The virtual environment must be activated before running this script.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Installing repo-auditor..."
python -m pip install -e "$PROJECT_ROOT"

echo "Running tests..."
python -m pytest
