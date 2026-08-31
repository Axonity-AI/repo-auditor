"""Command-line interface for repo-auditor



This module provides the user-facing CLI for running repository audits.

The CLI accepts a repository path, runs the RepositoryAuditor, and
displays the resulting check statuses using either human-readable or
JSON output.

The process exits with the status returned by the auditor so that the
CLI can be used directly in local development and automated CI
environments.
"""

from pathlib import Path

import click

from repo_auditor.auditor import RepositoryAuditor
from repo_auditor.output import format_human, format_json


@click.command()
@click.argument(
    "repo_path",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        path_type=Path,
    ),
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output results as JSON.",
)
def main(repo_path: Path, json_output: bool) -> None:
    """Audit a repository against Axonity engineering standards."""

    auditor = RepositoryAuditor(repo_path)
    results = auditor.audit()

    if json_output:
        click.echo(format_json(results))
    else:
        click.echo(format_human(results))

    raise SystemExit(auditor.get_exit_code(results))


if __name__ == "__main__":
    main()
