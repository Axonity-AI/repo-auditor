# ADR 0002: Repository Audit Design Decisions

**Status:** Proposed

**Date:** 2026-09-03

## Context

Repo Auditor is designed to audit repositories against Axonity's engineering standards. The tool needs consistent behavior across repositories with different technology stacks while remaining simple enough to maintain as additional checks are added.

The Week 0 warmup identifies five design decisions that need to be made during implementation:

1. Partial satisfaction and pass semantics
2. Exit code semantics
3. Handling non-Python repositories
4. Hard-coded checks versus configuration-driven checks
5. Output format

These decisions affect how audit results are interpreted, how the CLI behaves in automated environments, and how the tool can support different repositories.

## Decision

### 1. Partial satisfaction and pass semantics

A check passes only when the repository satisfies the condition defined by that check. Partial satisfaction does not result in a pass.

Each check returns one `CheckResult` with a status of `PASS`, `FAIL`, `WARNING`, or `NOT_APPLICABLE`. The checks implemented by Repo Auditor currently use `PASS` when their required condition is satisfied and `FAIL` when it is not.

This keeps the result of each check as absolute and avoids treating incomplete compliance as successful. This ensures non compliant repos from not passing.

### 2. Exit code semantics

The CLI returns exit code `0`  when all checks pass and exit code `1` when at least one check fails.

Warnings and not-applicable results do not cause a non-zero exit code.

This allows Repo Auditor to be used in scripts and CI pipelines where a non-zero exit code can indicate that a repository has failed an audit.

### 3. Handling non-Python repositories

Repo Auditor does not attempt to automatically determine the repository's programming language or technology stack.

Where a check has language-specific alternatives, the check recognizes the appropriate supported tools. For example, the type-check gate accepts either `mypy` for Python repositories or `tsc` for TypeScript repositories.

This allows the same auditor to work with different repository stacks without requiring separate repository configuration or unreliable language detection.

### 4. Hard-coded checks versus configuration-driven checks

The audit requirements are defined directly in the checks instead of using repository-specific configuration.

Each check evaluates one Axonity engineering requirement.

This keeps the tool simple and ensures all repositories are checked against the same standards.

The structure also allows for configuration driven checks to be added after.

### 5. Output format

Repo Auditor supports both human-readable and JSON output.

Human-readable output is the default and is intended for developers running the auditor directly from a terminal. JSON output is available through the `--json` option and provides structured results that can be consumed by scripts or other tooling.

Both formats represent the same underlying `CheckResult` data.

## Alternatives considered

- **Use partial or percentage-based compliance for individual checks** — Rejected because it would make pass/fail behavior less predictable and could allow incomplete compliance to appear successful.

- **Return different exit codes for every status** — Rejected because the primary use case is determining whether the repository passed the audit. A simple zero/non-zero distinction is easier to use in CI and automation.

- **Automatically detect the repository's language and select checks** — Rejected because repositories may contain multiple languages or frameworks, making automatic detection unreliable. Recognizing supported tools such as `mypy` and `tsc` is simpler.

- **Use repository-specific configuration for all checks** — Rejected for the initial implementation because it adds configuration and maintenance overhead and could allow repositories to define away required Axonity standards.

- **Provide only human-readable output** — Rejected because structured output is useful for automation and future integrations.

- **Provide only JSON output** — Rejected because the primary interactive use case is developers running the tool locally, where readable terminal output is more useful.

## Consequences

The audit behavior is predictable and consistent across repositories. Developers can understand exactly why an individual check passed or failed, and CI systems can rely on the exit code to determine whether the audit succeeded.

Supporting both `mypy` and `tsc` allows the auditor to work with Python and TypeScript repositories without requiring language detection.

Hard-coded standards make the initial implementation easier to understand and maintain, but adding support for substantially different repository types or organization-specific rules may eventually require a configuration-driven approach.

Supporting both human-readable and JSON output increases the usefulness of the CLI but requires maintaining two representations of the same audit results.

The strict pass/fail behavior also means that repositories that use an unsupported tool or only partially satisfy a requirement may fail the corresponding check until that tool or behavior is explicitly supported.
