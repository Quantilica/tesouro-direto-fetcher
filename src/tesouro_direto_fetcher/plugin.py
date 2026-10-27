"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from quantilica.cli.sdk import FetcherApp

from tesouro_direto_fetcher.constants import (
    DATASET_BUYBACKS,
    DATASET_INVESTORS,
    DATASET_MINT_STOCK,
    DATASET_OPERATIONS,
    DATASET_PRICES_RATES,
    DATASET_SALES,
)
from tesouro_direto_fetcher.storage import DataRepository

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


def convert(
    input_dir: Path,
    lake_dir: Path,
    *,
    dataset: list[str] | None = None,
    force: bool = False,
) -> Any:
    """Convert the raw microdata under ``input_dir`` into the lake at ``lake_dir``.

    The lake module needs the ``analysis`` extra, so it is imported on demand;
    the ``ImportError`` is handled by the ``convert`` and ``pipeline`` commands.
    """
    from tesouro_direto_fetcher import lake

    return lake.converter.convert(input_dir, lake_dir, datasets=dataset, force=force)


fetcher.command_convert(convert)
fetcher.command_pipeline(convert)
