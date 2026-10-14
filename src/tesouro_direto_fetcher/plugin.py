"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Annotated, Any

import typer
from quantilica.cli.sdk import FetcherApp
from quantilica.cli.ui import get_console, setup_rich_logging

from tesouro_direto_fetcher.constants import (
    DATASET_BUYBACKS,
    DATASET_INVESTORS,
    DATASET_MINT_STOCK,
    DATASET_OPERATIONS,
    DATASET_PRICES_RATES,
    DATASET_SALES,
)
from tesouro_direto_fetcher.storage import DataRepository

console = get_console()

GROUPS = {
    DATASET_PRICES_RATES: {"name": "Taxas dos Títulos Ofertados"},
    DATASET_OPERATIONS: {"name": "Operações do Tesouro Direto"},
    DATASET_INVESTORS: {"name": "Investidores do Tesouro Direto"},
    DATASET_MINT_STOCK: {"name": "Estoque do Tesouro Direto"},
    DATASET_BUYBACKS: {"name": "Resgates do Tesouro Direto"},
    DATASET_SALES: {"name": "Vendas do Tesouro Direto"},
}

GROUP_ALIASES = {
    "prices": [DATASET_PRICES_RATES],
    "operations": [DATASET_OPERATIONS],
    "investors": [DATASET_INVESTORS],
    "stock": [DATASET_MINT_STOCK],
    "buybacks": [DATASET_BUYBACKS],
    "sales": [DATASET_SALES],
    "all": [
        DATASET_PRICES_RATES,
        DATASET_OPERATIONS,
        DATASET_INVESTORS,
        DATASET_MINT_STOCK,
        DATASET_BUYBACKS,
        DATASET_SALES,
    ],
}


def list_datasets(group: str) -> list[dict[str, Any]]:
    """Fetch the list of datasets for a given group from the CKAN API.

    Args:
        group (str): The dataset group ID to query.

    Returns:
        list[dict[str, Any]]: A list of dataset dictionaries containing their metadata.
    """
    from quantilica.core.http import HttpClient

    from tesouro_direto_fetcher.constants import CKAN_API_URL

    client = HttpClient(timeout=60.0)
    try:
        params = {"id": group}
        data = client.get_json(CKAN_API_URL, params=params)
        if not data.get("success"):
            return []
        resources = data["result"]["resources"]
    except Exception:
        return []

    entries = []
    for r in resources:
        if r.get("format", "").upper() != "CSV":
            continue
        entries.append(
            {
                "id": r.get("name"),
                "url": r["url"],
                "ext": "csv",
                "group": group,
                "ckan_resource": r,
            }
        )
    return entries


def path_builder(
    output_dir: Path, entry: dict[str, Any], last_modified: dt.date | None
) -> Path:
    """Build the destination path for a given dataset entry.

    Args:
        output_dir (Path): The base output directory.
        entry (dict[str, Any]): The dataset entry metadata.
        last_modified (dt.date | None): The last modified date.

    Returns:
        Path: The constructed output path.
    """
    return DataRepository(output_dir).path_for_entry(entry, last_modified=last_modified)


fetcher = FetcherApp(
    name="tesouro-direto-fetcher",
    help="Dados do Tesouro Direto (preços, taxas, operações).",
    groups_dict=GROUPS,
    aliases_dict=GROUP_ALIASES,
    list_datasets=list_datasets,
    path_builder=path_builder,
)

app = fetcher.app


@app.command("convert")
def cmd_convert(
    data_dir: Annotated[
        Path,
        typer.Argument(help="Diretório de dados (raiz da árvore <dataset_id>/)"),
    ],
    verbose: Annotated[bool, typer.Option("--verbose", help="Logs detalhados")] = False,
) -> None:
    """Converter CSVs mais recentes para Parquet (requer extras de análise)."""
    setup_rich_logging(verbose, console=console)
    _convert_dir(data_dir)


def _convert_dir(data_dir: Path) -> None:
    """Converter os CSVs mais recentes de ``data_dir`` para Parquet."""
    try:
        from tesouro_direto_fetcher import converter
    except ImportError:
        console.print(
            "[red]Erro:[/red] convert requer extras de análise:"
            " quantilica install td --extra analysis"
        )
        raise typer.Exit(1) from None

    if not data_dir.is_dir():
        console.print(f"[red]Erro:[/red] diretório '{data_dir}' não existe.")
        raise typer.Exit(1)

    repo = DataRepository(data_dir)
    for dataset_id in repo.list_datasets():
        for fp in repo.get_all_latest_files(dataset_id):
            output_path = converter.convert_to_parquet(fp)
            console.print(f"  [green]✓[/green] {fp.name} → {output_path.name}")
