"""
Development environment management script.

Usage:
    python scripts/manage.py --setup
    python scripts/manage.py --install
    python scripts/manage.py --test
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Directory containing this script.
SCRIPT_DIR = Path(__file__).resolve().parent

# Root directory of the Repo Auditor source code.
SOURCE_ROOT = SCRIPT_DIR.parent

# Directory where the development virtual environment will be created.
# This uses the directory where the current terminal is located.
DEV_VENV_DIR = Path.cwd() / ".venv"

REQUIREMENTS_FILE = SOURCE_ROOT / "requirements.txt"


def run_command(command: list[str], cwd: Path | None = None) -> None:
    """Run a command and stop if it fails."""
    print(f"\n> {' '.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def setup() -> None:
    """Create and configure the development environment."""
    print(f"Setting up development environment in: {DEV_VENV_DIR}")

    # Create the virtual environment in the current terminal directory.
    if not DEV_VENV_DIR.exists():
        print("Creating virtual environment...")
        run_command([sys.executable, "-m", "venv", str(DEV_VENV_DIR)])
    else:
        print("Virtual environment already exists.")

    # Select the Python executable inside the new virtual environment.
    if sys.platform == "win32":
        venv_python = DEV_VENV_DIR / "Scripts" / "python.exe"
    else:
        venv_python = DEV_VENV_DIR / "bin" / "python"

    if not venv_python.exists():
        raise RuntimeError(f"Could not find virtual environment Python at {venv_python}")

    # Upgrade pip.
    print("Upgrading pip...")
    run_command([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])

    # Install project requirements.
    if REQUIREMENTS_FILE.exists():
        print("Installing requirements...")
        run_command(
            [
                str(venv_python),
                "-m",
                "pip",
                "install",
                "-r",
                str(REQUIREMENTS_FILE),
            ]
        )
    else:
        print(f"Warning: {REQUIREMENTS_FILE} was not found.")

    # Install Repo Auditor in editable mode.
    print("Installing Repo Auditor in editable mode...")
    run_command(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "-e",
            str(SOURCE_ROOT),
        ]
    )

    # Install pre-commit hooks.
    print("Installing pre-commit hooks...")
    run_command(
        [
            str(venv_python),
            "-m",
            "pre_commit",
            "install",
        ],
        cwd=SOURCE_ROOT,
    )

    # Install commit-msg hook if supported by the repository.
    commit_msg_config = SOURCE_ROOT / ".pre-commit-config.yaml"

    if commit_msg_config.exists():
        print("Installing commit-msg hook...")
        run_command(
            [
                str(venv_python),
                "-m",
                "pre_commit",
                "install",
                "--hook-type",
                "commit-msg",
            ],
            cwd=SOURCE_ROOT,
        )

    print("\nDevelopment environment setup complete.")
    print(f"Virtual environment: {DEV_VENV_DIR}")


def install() -> None:
    """Install Repo Auditor globally using pipx."""
    print("Checking for pipx...")

    try:
        subprocess.run(
            ["pipx", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("pipx is not installed or is not available in PATH.\nInstall pipx first, then run this command again.")

    print("Installing Repo Auditor with pipx...")

    run_command(
        [
            "pipx",
            "install",
            str(SOURCE_ROOT),
        ]
    )

    if REQUIREMENTS_FILE.exists():
        print("Injecting project requirements...")
        run_command(
            [
                "pipx",
                "inject",
                "repo-auditor",
                "--requirement",
                str(REQUIREMENTS_FILE),
            ]
        )

    print("\nRepo Auditor installed successfully.")


def test() -> None:
    """Run the project's test suite using the development environment."""
    if sys.platform == "win32":
        venv_python = DEV_VENV_DIR / "Scripts" / "python.exe"
    else:
        venv_python = DEV_VENV_DIR / "bin" / "python"

    if not venv_python.exists():
        print("Development environment not found.\nRun '--setup' first.")
        return

    print("Running tests...")
    run_command(
        [
            str(venv_python),
            "-m",
            "pytest",
        ],
        cwd=SOURCE_ROOT,
    )


def main() -> None:
    """Parse command-line arguments and run the selected action."""
    parser = argparse.ArgumentParser(description="Manage the Repo Auditor development environment.")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--setup",
        action="store_true",
        help="Create and configure the development environment.",
    )

    group.add_argument(
        "--install",
        action="store_true",
        help="Install Repo Auditor globally using pipx.",
    )

    group.add_argument(
        "--test",
        action="store_true",
        help="Run the test suite.",
    )

    args = parser.parse_args()

    if args.setup:
        setup()
    elif args.install:
        install()
    elif args.test:
        test()


if __name__ == "__main__":
    main()
