"""Convert the raw Tesouro Direto microdata into the Hive-partitioned lake.

Only the two microdata datasets (investors and operations) go to the lake. Each
raw CSV lands in ``<lake>/tesouro-direto/<dataset_id>/periodo=<periodo>/`` as
``<file_key>.parquet``; the period comes from the file name
(``...-de-2019@...csv`` -> ``periodo=2019``, ``...-ate-2017@...csv`` ->
``periodo=ate-2017``). Columns are kept as text with normalized names.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

try:
    import duckdb
    from quantilica.analytics.lake import LakeError, LakeWriter
    from quantilica.core.lake import DatasetDescriptor, file_key
except ImportError as exc:
    raise ImportError(
        "tesouro_direto_fetcher.lake requer o extra 'analysis': "
        "uv add 'tesouro-direto-fetcher[analysis]' "
        "--index https://index.quantilica.com/simple/"
    ) from exc

from tesouro_direto_fetcher import __version__
from tesouro_direto_fetcher.constants import DATASET_INVESTORS, DATASET_OPERATIONS
from tesouro_direto_fetcher.storage import DataRepository

SOURCE_ID = "tesouro-direto"
PARTITION_KEY = "periodo"

_PERIODO = re.compile(r"-(?P<kind>ate|de)-(?P<year>\d{4})$")


@dataclass(frozen=True)
class DatasetSpec:
    """How one raw dataset is read and registered in the lake."""

    dataset_id: str
    alias: str
    required: tuple[str, ...]
    separator: str = ";"
    encoding: str = "utf-8"
    header: bool = True
    rename: dict[str, str] = field(default_factory=dict)


SPECS: dict[str, DatasetSpec] = {
    DATASET_INVESTORS: DatasetSpec(
        dataset_id=DATASET_INVESTORS,
        alias="investidores",
        rename={"idade": "idade_do_investidor"},
        required=("codigo_do_investidor", "data_de_adesao", "idade_do_investidor"),
    ),
    DATASET_OPERATIONS: DatasetSpec(
        dataset_id=DATASET_OPERATIONS,
        alias="operacoes",
        required=("codigo_do_investidor", "data_da_operacao", "valor_da_operacao"),
    ),
}

_BY_NAME = {
    name: spec for spec in SPECS.values() for name in (spec.dataset_id, spec.alias)
}


@dataclass
class ConvertResult:
    """Counts of a conversion run; ``errors`` holds one message per failure."""

    converted: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def periodo_from_name(path: Path | str) -> str | None:
    """Return the ``periodo`` partition value for a raw file, if its name has one.

    ``investidores-do-tesouro-direto-de-2019@20261021.csv`` -> ``2019``;
    ``investidores-do-tesouro-direto-ate-2017@20261021.csv`` -> ``ate-2017``.
    """
    match = _PERIODO.search(file_key(path))
    if match is None:
        return None
    year = match["year"]
    return f"ate-{year}" if match["kind"] == "ate" else year


class LakeConverter:
    """Converter registered under the ``quantilica.lake`` entry point."""

    source_id = SOURCE_ID

    def datasets(self) -> list[str]:
        """Dataset ids this converter writes to the lake."""
        return list(SPECS)

    def convert(
        self,
        input_dir: Path,
        lake_dir: Path,
        *,
        datasets: list[str] | None = None,
        force: bool = False,
    ) -> ConvertResult:
        """Convert the latest raw file of each period into ``lake_dir``.

        Args:
            input_dir: Root of the raw data tree (``<dataset_id>/<file>.csv``).
            lake_dir: Root of the lake.
            datasets: Dataset ids or aliases to convert; ``None`` converts all.
            force: Reconvert even when the raw file's sha256 is already in the lake.

        Returns:
            ConvertResult: Files converted, skipped and the error messages.
        """
        input_dir = Path(input_dir)
        lake_dir = Path(lake_dir)
        result = ConvertResult()
        if not input_dir.is_dir():
            result.errors.append(f"diretório '{input_dir}' não existe")
            return result

        specs: list[DatasetSpec] = []
        for name in datasets or list(SPECS):
            spec = _BY_NAME.get(name)
            if spec is None:
                result.errors.append(f"dataset desconhecido: {name}")
            elif spec not in specs:
                specs.append(spec)

        repo = DataRepository(input_dir)
        for spec in specs:
            self._convert_dataset(repo, spec, lake_dir, force, result)
        return result

    def _convert_dataset(
        self,
        repo: DataRepository,
        spec: DatasetSpec,
        lake_dir: Path,
        force: bool,
        result: ConvertResult,
    ) -> None:
        files = sorted(repo.get_all_latest_files(spec.dataset_id))
        if not files:
            return
        writer = LakeWriter(
            lake_dir / SOURCE_ID / spec.dataset_id,
            DatasetDescriptor(
                source_id=SOURCE_ID,
                dataset_id=spec.dataset_id,
                alias=spec.alias,
                partition_keys=[PARTITION_KEY],
                partition_types={PARTITION_KEY: "varchar"},
            ),
            force=force,
        )
        for path in files:
            try:
                written = writer.write_duckdb(
                    path,
                    partitions={PARTITION_KEY: periodo_from_name(path)},
                    separator=spec.separator,
                    encoding=spec.encoding,
                    header=spec.header,
                    rename=spec.rename,
                    required=spec.required,
                    converter=f"tesouro-direto-fetcher {__version__}",
                )
            except (LakeError, OSError, duckdb.Error) as exc:
                message = str(exc).strip()
                first_line = message.splitlines()[0] if message else repr(exc)
                result.errors.append(f"{path.name}: {first_line}")
                continue
            if written.status == "skipped":
                result.skipped += 1
            else:
                result.converted += 1


converter = LakeConverter()
