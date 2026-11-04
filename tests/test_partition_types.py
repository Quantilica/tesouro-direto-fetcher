"""A chave de partição ``periodo`` segue o tipo canônico do core (texto)."""

from __future__ import annotations

import pytest

pytest.importorskip("quantilica.analytics.lake")
pytest.importorskip("duckdb")

from quantilica.core.lake import partition_types_for  # noqa: E402

from tesouro_direto_fetcher.lake import PARTITION_KEY  # noqa: E402


def test_periodo_continua_varchar() -> None:
    assert partition_types_for([PARTITION_KEY]) == {PARTITION_KEY: "varchar"}
    assert partition_types_for([]) == {}
