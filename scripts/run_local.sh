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
python -m pip install -q -r "$PROJECT_ROOT/requirements.txt"

echo "Installing the project in editable mode as a working CLI..."
python -m pip install -e .

export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
elif [ -f "$PROJECT_ROOT/.env.example" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env.example" | xargs)
fi
