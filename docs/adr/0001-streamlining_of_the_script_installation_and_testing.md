# ADR 0001: Streamlining of the script installation and testing

**Status:** Proposed

**Date:** 2026-08-28

## Context

Repo Auditor needs to support two use cases: developers working on the project and users who only want to install and use the Repo Auditor CLI to audit other repositories.

The development workflow requires a project-local virtual environment, development dependencies, editable installation, and pre-commit hooks. CLI users need Repo Auditor and its runtime dependencies to be isolated from the system Python environment while still being available as a globally accessible command.

The project should also work across Windows, Linux, macOS, WSL, Bash, and PowerShell without maintaining separate workflow logic for each shell.

## Decision

Use a single cross-platform Python management script with flags for development setup, global CLI installation, and testing.

The development workflow will create and use a project-local `.venv`, install development dependencies, install Repo Auditor in editable mode, and configure pre-commit hooks.

Global CLI installation will use `pipx`. The management script will run `pipx install .` to install Repo Auditor into an isolated virtual environment and make the `repo-auditor` command globally available.

The management script will check whether `pipx` is installed before attempting the CLI installation. If `pipx` is not available, it will provide the user with the command to install it and instruct them to rerun the installation command.

## Alternatives considered

- **Separate Bash and PowerShell scripts** — Rejected because this duplicates workflow logic and requires users to choose the correct script for their shell.

- **Install all dependencies globally** — Rejected because it can pollute the system Python environment and cause dependency conflicts.


- **Use a custom virtual environment and PATH management** — Rejected because it requires Repo Auditor to maintain platform and shell specific PATH configuration. This implementation would be obsolete when pipx does the same with more efficient code.

- **Use the development virtual environment for global CLI usage** — Rejected because users who only want to audit repositories should not need the full development environment.

## Consequences

- Users must have `pipx` installed before using the global CLI installation command. If it is not installed, the management script will provide the required installation command.

- Developers have a single cross-platform command for setting up and testing Repo Auditor.

- CLI users can install Repo Auditor into a dedicated virtual environment and use the `repo-auditor` command from any directory without modifying the system Python environment.

- The project now maintains two separate virtual environments when both workflows are used: one for development and one for the globally available CLI.
