from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from geneweb.adapters.ocaml_bridge.bridge import OcamlCommandError, run_ged2gwb, run_gwb2ged

app = typer.Typer(add_completion=False, help="CLI GeneWeb (pont OCaml et commandes Python)")


@app.callback()
def _version(ctx: typer.Context) -> None:
    """Entry point for future global options."""


@app.command()
def gwb2ged(
    input_dir: Annotated[
        Path, typer.Option(exists=True, file_okay=False, readable=True, help="Répertoire base GWB")
    ],
    output_file: Annotated[
        Path, typer.Option(dir_okay=False, writable=True, help="Fichier GEDCOM de sortie")
    ],
) -> None:
    try:
        out = run_gwb2ged(["-i", str(input_dir), "-o", str(output_file)])
        typer.echo(out)
    except OcamlCommandError as e:
        typer.echo(e.stderr, err=True)
        raise typer.Exit(e.returncode) from e


@app.command()
def ged2gwb(
    input_file: Annotated[
        Path, typer.Option(exists=True, file_okay=True, readable=True, help="GEDCOM d'entrée")
    ],
    output_dir: Annotated[Path, typer.Option(file_okay=False, help="Répertoire GWB cible")],
) -> None:
    try:
        out = run_ged2gwb(["-i", str(input_file), "-o", str(output_dir)])
        typer.echo(out)
    except OcamlCommandError as e:
        typer.echo(e.stderr, err=True)
        raise typer.Exit(e.returncode) from e


if __name__ == "__main__":
    app()

def main() -> None:
    app()
