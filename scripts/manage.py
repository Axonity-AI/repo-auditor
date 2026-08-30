"""
manage.py - Cross-platform management utility for Repo Auditor.

Usage:
    python scripts/manage.py --setup
    python scripts/manage.py --install
    python scripts/manage.py --test
"""

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Get the directory containing this script and the project root.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Virtual environment used for local development.
DEV_VENV_DIR = PROJECT_ROOT / ".venv"


def get_venv_python(venv_dir: Path) -> Path:
    """Return the Python executable for a virtual environment."""

    # Windows stores the Python executable in the Scripts directory.
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "python.exe"

    # macOS and Linux use the bin directory.
    return venv_dir / "bin" / "python"


def run(*args: str) -> None:
    """Run a command and stop if it fails."""

    # check=True causes the script to stop if the command fails.
    subprocess.run(args, check=True)


def setup() -> None:
    """Set up Repo Auditor for local development."""
    python = get_venv_python(DEV_VENV_DIR)

    print("Setting up Repo Auditor for development...")

    # Create the development virtual environment if it doesn't exist.
    if not DEV_VENV_DIR.exists():
        print("Creating development virtual environment...")
        run(sys.executable, "-m", "venv", str(DEV_VENV_DIR))

    # Upgrade pip inside the development environment.
    print("Upgrading pip...")
    run(str(python), "-m", "pip", "install", "--upgrade", "pip")

    # Install the project's development dependencies.
    print("Installing development dependencies...")
    run(
        str(python),
        "-m",
        "pip",
        "install",
        "-r",
        str(PROJECT_ROOT / "requirements.txt"),
    )

    # Install Repo Auditor in editable mode so source changes are
    # immediately reflected without reinstalling the package.
    print("Installing Repo Auditor in editable mode...")
    run(
        str(python),
        "-m",
        "pip",
        "install",
        "-e",
        str(PROJECT_ROOT),
    )

    # Install the standard pre-commit hook.
    print("Installing pre-commit hooks...")
    run(str(python), "-m", "pre_commit", "install")

    # Install the commit-msg hook used for commit message checks.
    run(
        str(python),
        "-m",
        "pre_commit",
        "install",
        "--hook-type",
        "commit-msg",
    )

    print("\nDevelopment setup complete.")


def install() -> None:
    """Install Repo Auditor as a globally available CLI using pipx."""

    print("Installing Repo Auditor as a global CLI...")

    # Check whether pipx is already available on the user's PATH.
    pipx = shutil.which("pipx")

    if pipx is None:
        print("pipx is not installed.")
        print("Install it with:")
        print("  python -m pip install pipx")
        print("\nThen run this command again:")
        print("  python scripts/manage.py --install")
        sys.exit(1)

    # pipx creates and manages an isolated virtual environment for
    # Repo Auditor and handles making the CLI available on PATH.
    run(pipx, "install", str(PROJECT_ROOT))

    print("\nRepo Auditor installed successfully.")


def test() -> None:
    """Run the test suite using the development virtual environment."""
    python = get_venv_python(DEV_VENV_DIR)

    # Make sure the development environment has been set up first.
    if not python.exists():
        print("Development environment not found.")
        print("Run:")
        print("  python scripts/manage.py --setup")
        sys.exit(1)

    print("Running tests...")

    # Run pytest using the project's development environment.
    run(str(python), "-m", "pytest")


def main() -> None:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Manage the Repo Auditor development and CLI environments.")

    # Only one management operation can be selected at a time.
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--setup",
        action="store_true",
        help="Set up Repo Auditor for development.",
    )

    group.add_argument(
        "--install",
        action="store_true",
        help="Install Repo Auditor as a globally available CLI using pipx.",
    )

    group.add_argument(
        "--test",
        action="store_true",
        help="Run the test suite.",
    )

    args = parser.parse_args()

    # Run the function corresponding to the selected command.
    if args.setup:
        setup()
    elif args.install:
        install()
    elif args.test:
        test()


if __name__ == "__main__":
    # Start the CLI when this file is executed directly.
    main()
