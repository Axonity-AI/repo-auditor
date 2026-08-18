#!/bin/bash
# run_local.sh - creates venv, installs deps, loads env, runs the app in dev mode
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install -q -r "$PROJECT_ROOT/requirements.txt"

export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
elif [ -f "$PROJECT_ROOT/.env.example" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env.example" | xargs)
fi

# TODO: replace with the actual app entrypoint, e.g.:
#   python -m {{PACKAGE_NAME}}.main
echo "TODO: set the app entrypoint in scripts/run_local.sh"
