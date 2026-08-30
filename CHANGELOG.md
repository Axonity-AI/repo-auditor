# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.2.0] - 2026-08-27

### Added

- Added `manage.py`, a script that gives users options to set up the project for development, install Repo Auditor as a CLI, or run the test suite using the appropriate virtual environment.
- Added `bump_version.py`, a script that supports major, minor, and patch version updates, as well as setting the version to a specific value. It updates the version in `pyproject.toml`, `README.md`, and `CHANGELOG.md`.

### Changed

- docs/ADR to include more information on proposed overhaul of scripts/ and README.md
- Updated `scripts/run_local.sh` to install a working version of the CLI.
- Added a script that runs all the tests (`run_tests.sh`).
- Added a script to automatically update the version number across the repository depending on the change.
- Centralized the version number to only `pyproject.toml`, and `README.md`.



## [1.1.0] - 2026-08-24

### Added

- Added foundation for CLI and repository audit.
- Added CODEOWNERS, LICENSE, and SECURITY.md checks.
- Added human readable and JSON output under output.py.
- Added tests for the new checks and CLI.


## [1.0.1] - 2026-08-23

### Added

- Added dedicated components for the packages under src.
- Added a dedicated section for tests under tests/.
- Added documentation for "__init.py__" under src/repo_auditor, tests/

### Changed

- Replaced project-template placeholders "{{PACKAGE_NAME}}" with the "repo_auditor" package identity.
- Updated package metadata and documentation in "SECURITY.md", "pyproject.toml", "Readme.md", "LICENSE.md" and the docker files. This was done to reflect the Repo Auditor project.

## [1.0.0] - 2026-08-21

### Added

- Added `CHANGELOG.md` to provide a centralized record of repository changes.
