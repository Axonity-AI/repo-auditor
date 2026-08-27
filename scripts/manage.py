"""
manage.py - Cross-platform management utility for Repo Auditor.

Usage:
    python scripts/manage.py --setup
    python scripts/manage.py --install
    python scripts/manage.py --test
"""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DEV_VENV_DIR = PROJECT_ROOT / ".venv"
CLI_VENV_DIR = Path.home() / ".repo-auditor"


def get_venv_python(venv_dir: Path) -> Path:
    """Return the Python executable for a virtual environment."""
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "python.exe"

    return venv_dir / "bin" / "python"


def run(*args: str) -> None:
    """Run a command and stop if it fails."""
    subprocess.run(args, check=True)


def setup() -> None:
    """Set up Repo Auditor for local development."""
    python = get_venv_python(DEV_VENV_DIR)

    print("Setting up Repo Auditor for development...")

    if not DEV_VENV_DIR.exists():
        print("Creating development virtual environment...")
        run(sys.executable, "-m", "venv", str(DEV_VENV_DIR))

    print("Upgrading pip...")
    run(str(python), "-m", "pip", "install", "--upgrade", "pip")

    print("Installing development dependencies...")
    run(
        str(python),
        "-m",
        "pip",
        "install",
        "-r",
        str(PROJECT_ROOT / "requirements.txt"),
    )

    print("Installing Repo Auditor in editable mode...")
    run(
        str(python),
        "-m",
        "pip",
        "install",
        "-e",
        str(PROJECT_ROOT),
    )

    print("Installing pre-commit hooks...")
    run(str(python), "-m", "pre_commit", "install")
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
    """Install Repo Auditor into a dedicated global CLI environment."""
    python = get_venv_python(CLI_VENV_DIR)

    print("Installing Repo Auditor as a global CLI...")

    if not CLI_VENV_DIR.exists():
        print("Creating dedicated CLI environment...")
        run(sys.executable, "-m", "venv", str(CLI_VENV_DIR))

    print("Installing Repo Auditor...")
    run(
        str(python),
        "-m",
        "pip",
        "install",
        "--upgrade",
        str(PROJECT_ROOT),
    )

    if platform.system() == "Windows":
        cli_dir = CLI_VENV_DIR / "Scripts"
    else:
        cli_dir = CLI_VENV_DIR / "bin"

    update_path(cli_dir)

    print("\nRepo Auditor installed successfully.")
    print(f"CLI location: {cli_dir}")
    print("Restart your terminal if the repo-auditor command is not immediately available.")


def update_path(cli_dir: Path) -> None:
    """Add the CLI directory to the user's PATH if necessary."""
    cli_dir = cli_dir.resolve()
    cli_dir_str = str(cli_dir)

    current_path = os.environ.get("PATH", "")

    if cli_dir_str in current_path.split(os.pathsep):
        return

    system = platform.system()

    if system == "Windows":
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            "Environment",
            0,
            winreg.KEY_READ | winreg.KEY_WRITE,
        ) as key:
            try:
                existing_path, _ = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                existing_path = ""

            paths = existing_path.split(";") if existing_path else []

            if cli_dir_str not in paths:
                paths.append(cli_dir_str)
                winreg.SetValueEx(
                    key,
                    "Path",
                    0,
                    winreg.REG_EXPAND_SZ,
                    ";".join(paths),
                )

    else:
        shell_config = Path.home() / ".profile"

        export_line = f'\nexport PATH="$PATH:{cli_dir_str}"\n'

        existing = shell_config.read_text() if shell_config.exists() else ""

        if export_line.strip() not in existing:
            with shell_config.open("a") as file:
                file.write(export_line)


def test() -> None:
    """Run the test suite using the development virtual environment."""
    python = get_venv_python(DEV_VENV_DIR)

    if not python.exists():
        print("Development environment not found.")
        print("Run:")
        print("  python scripts/manage.py --setup")
        sys.exit(1)

    print("Running tests...")
    run(str(python), "-m", "pytest")


def main() -> None:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Manage the Repo Auditor development and CLI environments.")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--setup",
        action="store_true",
        help="Set up Repo Auditor for development.",
    )

    group.add_argument(
        "--install",
        action="store_true",
        help="Install Repo Auditor as a globally available CLI.",
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
