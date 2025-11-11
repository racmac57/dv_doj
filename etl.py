from pathlib import Path

import click
from rich import print  # noqa: F401  # imported for side effects of rich printing

from etl_scripts import (
    ai_data_analyzer,
    export_excel_sheets_to_csv,
    map_dv_to_rms_locations,
    transform_dv_data,
    verify_transformations,
)


@click.group()
def cli() -> None:
    """Command-line entry point for domestic violence ETL workflows."""


@cli.command()
@click.option(
    "--src",
    default="raw_data/xlsx",
    type=click.Path(path_type=Path),
    show_default=True,
    help="Directory containing Excel workbooks.",
)
@click.option(
    "--out",
    default="output",
    type=click.Path(path_type=Path),
    show_default=True,
    help="Destination directory for CSV exports.",
)
def export(src: Path, out: Path) -> None:
    export_excel_sheets_to_csv.main(src, out)


@cli.command()
@click.option(
    "--src",
    default="output",
    type=click.Path(path_type=Path),
    show_default=True,
    help="Directory containing CSV/Excel files to profile.",
)
@click.option(
    "--out",
    default="analysis/ai_responses",
    type=click.Path(path_type=Path),
    show_default=True,
    help="Directory for analysis outputs.",
)
def profile(src: Path, out: Path) -> None:
    ai_data_analyzer.main(src, out)


@cli.command()
@click.option(
    "--src",
    default="processed_data",
    type=click.Path(path_type=Path),
    show_default=True,
    help="Source directory containing DV fixed files.",
)
@click.option(
    "--out",
    default="processed_data",
    type=click.Path(path_type=Path),
    show_default=True,
    help="Destination directory for transformed outputs.",
)
def transform(src: Path, out: Path) -> None:
    transform_dv_data.main(src, out)


@cli.command()
@click.option(
    "--src",
    default="processed_data",
    type=click.Path(path_type=Path),
    show_default=True,
    help="Directory with transformed DV data.",
)
@click.option(
    "--out",
    default="processed_data",
    type=click.Path(path_type=Path),
    show_default=True,
    help="Directory for mapped outputs.",
)
def map(src: Path, out: Path) -> None:
    map_dv_to_rms_locations.main(src, out)


@cli.command()
@click.option(
    "--src",
    default="processed_data",
    type=click.Path(path_type=Path),
    show_default=True,
    help="Directory containing transformed DV datasets.",
)
@click.option(
    "--out",
    default="logs",
    type=click.Path(path_type=Path),
    show_default=True,
    help="Directory to write verification reports.",
)
def verify(src: Path, out: Path) -> None:
    verify_transformations.main(src, out)


if __name__ == "__main__":
    cli()

