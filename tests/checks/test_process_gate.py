from repo_auditor.checks._process_gate import has_process_command


def test_detects_pytest() -> None:
    assert has_process_command("pytest", "test")


def test_detects_pytest_module() -> None:
    assert has_process_command("python -m pytest", "test")


def test_detects_unittest_module() -> None:
    assert has_process_command("python -m unittest", "test")


def test_detects_npm_test() -> None:
    assert has_process_command("npm test", "test")


def test_detects_npm_run_test() -> None:
    assert has_process_command("npm run test", "test")


def test_detects_make_test() -> None:
    assert has_process_command("make test", "test")


def test_detects_cargo_test() -> None:
    assert has_process_command("cargo test", "test")


def test_detects_test_script() -> None:
    assert has_process_command("./scripts/test.sh", "test")


def test_detects_ruff() -> None:
    assert has_process_command("ruff check .", "lint")


def test_detects_ruff_module() -> None:
    assert has_process_command("python -m ruff check .", "lint")


def test_detects_eslint() -> None:
    assert has_process_command("eslint .", "lint")


def test_detects_npm_lint() -> None:
    assert has_process_command("npm run lint", "lint")


def test_detects_make_lint() -> None:
    assert has_process_command("make lint", "lint")


def test_detects_lint_script() -> None:
    assert has_process_command("./scripts/lint.sh", "lint")


def test_ignores_echo_test() -> None:
    assert not has_process_command('echo "test"', "test")


def test_ignores_echo_lint() -> None:
    assert not has_process_command('echo "lint"', "lint")


def test_ignores_pytest_installation() -> None:
    assert not has_process_command("pip install pytest", "test")


def test_ignores_npm_installation() -> None:
    assert not has_process_command("npm install", "test")


def test_ignores_build_command_for_test() -> None:
    assert not has_process_command("npm run build", "test")


def test_ignores_build_command_for_lint() -> None:
    assert not has_process_command("npm run build", "lint")


def test_job_name_does_not_count_as_test() -> None:
    assert not has_process_command(
        "npm run build",
        "test",
        job_name="test",
    )


def test_step_name_does_not_count_as_test() -> None:
    assert not has_process_command(
        "npm run build",
        "test",
        step_name="Run tests",
    )


def test_handles_multiple_commands() -> None:
    assert has_process_command(
        "npm install && npm test",
        "test",
    )


def test_handles_multiple_commands_with_lint() -> None:
    assert has_process_command(
        "npm install && npm run lint",
        "lint",
    )


def test_ignores_empty_commands() -> None:
    assert not has_process_command("", "test")


def test_ignores_shell_no_op_commands() -> None:
    assert not has_process_command("true", "test")
    assert not has_process_command("false", "test")
    assert not has_process_command("cd tests", "test")
    assert not has_process_command("export TEST=true", "test")
