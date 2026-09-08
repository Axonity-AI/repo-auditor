"""Helpers for identifying process-oriented CI run steps used in test_gate.py and lint_gate.py."""

import re

_SHELL_NO_OPS = {
    ":",
    "cd",
    "echo",
    "export",
    "false",
    "printf",
    "set",
    "source",
    "true",
}

_INSTALL_COMMANDS = {
    "apt",
    "apt-get",
    "npm",
    "pip",
    "pip3",
    "pnpm",
    "yarn",
}


def has_process_command(
    run: str,
    process: str,
    *,
    job_name: str = "",
    step_name: str = "",
) -> bool:
    """Return whether a run step performs the requested process."""

    process = process.lower()

    # Split the run block into individual shell commands.
    commands = re.split(r"[\n;&|]+", run)

    for command in commands:
        words = command.strip().split()

        if not words:
            continue

        # Ignore environment variables and command flags.
        while words and ("=" in words[0] or words[0].startswith("-")):
            words.pop(0)

        if not words:
            continue

        executable = words[0].lower().rsplit("/", 1)[-1]
        arguments = [word.lower() for word in words[1:]]

        # Commands such as echo, cd, and export do not perform
        # linting or testing.
        if executable in _SHELL_NO_OPS:
            continue

        # Installing a tool is not the same as running it.
        if executable in _INSTALL_COMMANDS and arguments and arguments[0] == "install":
            continue

        # Python module commands.
        if executable in {"python", "python3"}:
            if len(arguments) >= 2 and arguments[0] == "-m":
                module = arguments[1]

                if process == "test" and module in {
                    "pytest",
                    "unittest",
                    "nose",
                    "nose2",
                }:
                    return True

                if process == "lint" and module in {
                    "ruff",
                    "pylint",
                    "flake8",
                    "black",
                }:
                    return True

        # npm, pnpm, and yarn scripts.
        if executable in {"npm", "pnpm", "yarn"}:
            if process == "test":
                if arguments[:1] == ["test"]:
                    return True
                if arguments[:2] == ["run", "test"]:
                    return True

            if process == "lint":
                if arguments[:1] == ["lint"]:
                    return True
                if arguments[:2] == ["run", "lint"]:
                    return True

        # Direct testing commands.
        if process == "test":
            if executable in {
                "pytest",
                "py.test",
                "jest",
                "mocha",
                "vitest",
            }:
                return True

            if executable == "cargo" and arguments[:1] == ["test"]:
                return True

            if executable == "make" and arguments[:1] == ["test"]:
                return True

        # Direct linting commands.
        if process == "lint":
            if executable in {
                "ruff",
                "pylint",
                "flake8",
                "eslint",
                "stylelint",
                "biome",
            }:
                return True

            if executable == "make" and arguments[:1] == ["lint"]:
                return True

        # Project-specific scripts such as ./scripts/test.sh.
        if executable.startswith("./") or executable.endswith(".sh"):
            if process in executable:
                return True

    return False
