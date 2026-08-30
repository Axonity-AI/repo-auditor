"""
bump_version.py - Bump or set the Repo Auditor version.

Usage:
    python scripts/bump_version.py --patch
    python scripts/bump_version.py --minor
    python scripts/bump_version.py --major
    python scripts/bump_version.py --set 2.0.0
"""

import argparse
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

FILES = [
    PROJECT_ROOT / "pyproject.toml",
    PROJECT_ROOT / "README.md",
]

SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def get_current_version() -> str:
    """Get the current version from pyproject.toml."""
    pyproject = PROJECT_ROOT / "pyproject.toml"
    content = pyproject.read_text()

    match = re.search(
        r'^version\s*=\s*"(\d+\.\d+\.\d+)"',
        content,
        re.MULTILINE,
    )

    if not match:
        raise ValueError("Could not find version in pyproject.toml.")

    return match.group(1)


def bump_version(version: str, bump_type: str) -> str:
    """Calculate the next semantic version."""
    major, minor, patch = map(int, version.split("."))

    if bump_type == "major":
        return f"{major + 1}.0.0"

    if bump_type == "minor":
        return f"{major}.{minor + 1}.0"

    return f"{major}.{minor}.{patch + 1}"


def update_file(path: Path, old_version: str, new_version: str) -> None:
    """Replace the current version with the new version."""
    content = path.read_text()

    if old_version not in content:
        raise ValueError(f"Version {old_version} was not found in {path}.")

    path.write_text(content.replace(old_version, new_version))


def main() -> None:
    """Parse arguments and update the project version."""
    parser = argparse.ArgumentParser(description="Bump or set the Repo Auditor version.")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--major",
        action="store_true",
        help="Bump major version: 1.2.3 -> 2.0.0",
    )

    group.add_argument(
        "--minor",
        action="store_true",
        help="Bump minor version: 1.2.3 -> 1.3.0",
    )

    group.add_argument(
        "--patch",
        action="store_true",
        help="Bump patch version: 1.2.3 -> 1.2.4",
    )

    group.add_argument(
        "--set",
        metavar="VERSION",
        help="Set an explicit version, e.g. 2.1.0",
    )

    args = parser.parse_args()

    current_version = get_current_version()

    if args.set:
        if not SEMVER_PATTERN.fullmatch(args.set):
            parser.error("Version must follow semantic versioning format: X.Y.Z")

        new_version = args.set
    elif args.major:
        new_version = bump_version(current_version, "major")
    elif args.minor:
        new_version = bump_version(current_version, "minor")
    else:
        new_version = bump_version(current_version, "patch")

    if current_version == new_version:
        parser.error("New version is the same as the current version.")

    for file in FILES:
        update_file(file, current_version, new_version)

    print(f"Version updated: {current_version} -> {new_version}")


if __name__ == "__main__":
    main()
