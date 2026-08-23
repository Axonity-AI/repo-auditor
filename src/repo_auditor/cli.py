"""Command-line interface for repo-auditor."""

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
