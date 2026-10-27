"""Tests for the Hive lake conversion of the Tesouro Direto microdata."""

from __future__ import annotations

from importlib.metadata import entry_points
from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")
pytest.importorskip("duckdb")

from quantilica.analytics.lake import check_dataset, scan_dataset  # noqa: E402
from typer.testing import CliRunner  # noqa: E402

from tesouro_direto_fetcher.constants import (  # noqa: E402
    DATASET_INVESTORS,
    DATASET_OPERATIONS,
)
from tesouro_direto_fetcher.lake import (  # noqa: E402
    SOURCE_ID,
    ConvertResult,
    converter,
    periodo_from_name,
)

INVESTORS_CSV = (
    "Código do Investidor;Data de Adesão;Estado Civil;Idade\n"
    "1;01/01/2019;Solteiro;30\n"
    "2;02/01/2019;Casado;45\n"
    "3;03/01/2019;Solteiro;27\n"
)
OPERATIONS_CSV = (
    "Código do Investidor;Data da Operação;Tipo Titulo;Valor da Operação\n"
    "1;05/01/2019;Tesouro Selic;1000,50\n"
    "2;06/01/2019;Tesouro IPCA+;250,00\n"
)
HTML_PAGE = "<!DOCTYPE html>\n<html><body>Service unavailable</body></html>\n"


def _write(root: Path, dataset_id: str, name: str, text: str) -> Path:
    path = root / dataset_id / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def raw(tmp_path: Path) -> Path:
    root = tmp_path / "raw"
    _write(
        root,
        DATASET_INVESTORS,
        "investidores-do-tesouro-direto-ate-2017@20261021.csv",
        INVESTORS_CSV,
    )
    _write(
        root,
        DATASET_INVESTORS,
        "investidores-do-tesouro-direto-de-2019@20261021.csv",
        INVESTORS_CSV,
    )
    _write(
        root,
        DATASET_OPERATIONS,
        "operacoes-do-tesouro-direto-de-2019@20261021.csv",
        OPERATIONS_CSV,
    )
    return root


@pytest.fixture
def lake(tmp_path: Path) -> Path:
    return tmp_path / "lake"


def _dataset_dir(lake: Path, dataset_id: str) -> Path:
    return lake / SOURCE_ID / dataset_id


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("investidores-do-tesouro-direto-de-2019@20261021.csv", "2019"),
        ("investidores-do-tesouro-direto-ate-2017@20261021T000000.csv", "ate-2017"),
        ("operacoes-do-tesouro-direto-de-2014.csv", "2014"),
        ("operacoes-do-tesouro-direto@20261021.csv", None),
    ],
)
def test_periodo_from_name(name: str, expected: str | None) -> None:
    assert periodo_from_name(name) == expected


def test_convert_writes_hive_layout(raw: Path, lake: Path) -> None:
    result = converter.convert(raw, lake)

    assert isinstance(result, ConvertResult)
    assert (result.converted, result.skipped, result.errors) == (3, 0, [])
    inv = _dataset_dir(lake, DATASET_INVESTORS)
    ops = _dataset_dir(lake, DATASET_OPERATIONS)
    assert (
        inv / "periodo=2019" / "investidores-do-tesouro-direto-de-2019.parquet"
    ).is_file()
    assert (
        inv / "periodo=ate-2017" / "investidores-do-tesouro-direto-ate-2017.parquet"
    ).is_file()
    assert (
        ops / "periodo=2019" / "operacoes-do-tesouro-direto-de-2019.parquet"
    ).is_file()
    assert (inv / "_dataset.json").is_file()


def test_convert_renames_and_normalizes_columns(raw: Path, lake: Path) -> None:
    converter.convert(raw, lake)

    investors = scan_dataset(_dataset_dir(lake, DATASET_INVESTORS)).collect()
    assert "idade_do_investidor" in investors.columns
    assert "idade" not in investors.columns
    assert {"codigo_do_investidor", "data_de_adesao", "periodo"} <= set(
        investors.columns
    )
    assert investors.height == 6
    operations = scan_dataset(_dataset_dir(lake, DATASET_OPERATIONS)).collect()
    assert {"data_da_operacao", "valor_da_operacao"} <= set(operations.columns)
    assert operations.height == 2


def test_converted_datasets_conform_to_contract(raw: Path, lake: Path) -> None:
    converter.convert(raw, lake)

    for dataset_id in (DATASET_INVESTORS, DATASET_OPERATIONS):
        assert check_dataset(_dataset_dir(lake, dataset_id)) == []


def test_second_run_skips_everything(raw: Path, lake: Path) -> None:
    converter.convert(raw, lake)
    again = converter.convert(raw, lake)

    assert (again.converted, again.skipped, again.errors) == (0, 3, [])


def test_force_reconverts(raw: Path, lake: Path) -> None:
    converter.convert(raw, lake)
    forced = converter.convert(raw, lake, force=True)

    assert (forced.converted, forced.skipped) == (3, 0)
    assert check_dataset(_dataset_dir(lake, DATASET_INVESTORS)) == []


def test_republished_file_replaces_instead_of_accumulating(
    raw: Path, lake: Path
) -> None:
    converter.convert(raw, lake)
    _write(
        raw,
        DATASET_OPERATIONS,
        "operacoes-do-tesouro-direto-de-2019@20261101.csv",
        OPERATIONS_CSV + "3;07/01/2019;Tesouro Prefixado;10,00\n",
    )

    result = converter.convert(raw, lake, datasets=["operacoes"])

    assert (result.converted, result.skipped) == (1, 0)
    ops = _dataset_dir(lake, DATASET_OPERATIONS)
    assert len(list(ops.rglob("*.parquet"))) == 1
    assert scan_dataset(ops).collect().height == 3


def test_html_error_page_is_rejected_and_others_continue(raw: Path, lake: Path) -> None:
    _write(
        raw,
        DATASET_INVESTORS,
        "investidores-do-tesouro-direto-de-2020@20261021.csv",
        HTML_PAGE,
    )

    result = converter.convert(raw, lake)

    assert result.converted == 3
    assert len(result.errors) == 1
    assert "investidores-do-tesouro-direto-de-2020@20261021.csv" in result.errors[0]
    inv = _dataset_dir(lake, DATASET_INVESTORS)
    assert not (inv / "periodo=2020").exists()
    assert check_dataset(inv) == []


def test_csv_with_wrong_header_is_rejected(raw: Path, lake: Path) -> None:
    _write(
        raw,
        DATASET_OPERATIONS,
        "operacoes-do-tesouro-direto-de-2021@20261021.csv",
        "foo;bar\n1;2\n",
    )

    result = converter.convert(raw, lake, datasets=[DATASET_OPERATIONS])

    assert result.converted == 1
    assert len(result.errors) == 1
    assert not (_dataset_dir(lake, DATASET_OPERATIONS) / "periodo=2021").exists()


def test_dataset_filter_accepts_alias_and_id(raw: Path, lake: Path) -> None:
    result = converter.convert(raw, lake, datasets=["operacoes"])

    assert result.converted == 1
    assert not _dataset_dir(lake, DATASET_INVESTORS).exists()
    by_id = converter.convert(raw, lake, datasets=[DATASET_INVESTORS])
    assert by_id.converted == 2


def test_unknown_dataset_is_reported_as_error(raw: Path, lake: Path) -> None:
    result = converter.convert(raw, lake, datasets=["nao-existe"])

    assert result.converted == 0
    assert result.errors == ["dataset desconhecido: nao-existe"]


def test_missing_input_dir_is_reported_as_error(tmp_path: Path, lake: Path) -> None:
    result = converter.convert(tmp_path / "ausente", lake)

    assert result.converted == 0
    assert len(result.errors) == 1


def test_entry_point_is_registered() -> None:
    names = {ep.name: ep.value for ep in entry_points(group="quantilica.lake")}
    assert names.get(SOURCE_ID) == "tesouro_direto_fetcher.lake:converter"


def test_cli_convert_end_to_end(raw: Path, lake: Path) -> None:
    from tesouro_direto_fetcher.plugin import app

    result = CliRunner().invoke(
        app,
        ["convert", "-i", str(raw), "--lake", str(lake), "--dataset", "investidores"],
    )

    assert result.exit_code == 0, result.output
    assert check_dataset(_dataset_dir(lake, DATASET_INVESTORS)) == []


def test_cli_convert_exits_1_on_errors(raw: Path, lake: Path) -> None:
    from tesouro_direto_fetcher.plugin import app

    _write(
        raw,
        DATASET_OPERATIONS,
        "operacoes-do-tesouro-direto-de-2022@20261021.csv",
        HTML_PAGE,
    )

    result = CliRunner().invoke(app, ["convert", "-i", str(raw), "--lake", str(lake)])

    assert result.exit_code == 1


def test_unreadable_csv_is_reported_without_aborting(raw: Path, lake: Path) -> None:
    bad = (
        raw / DATASET_INVESTORS / "investidores-do-tesouro-direto-de-2023@20261021.csv"
    )
    bad.write_bytes(b"C\xf3digo do Investidor;Data de Ades\xe3o;Idade\n1;2;3\n")

    result = converter.convert(raw, lake)

    assert result.converted == 3
    assert len(result.errors) == 1
    assert "de-2023" in result.errors[0]
