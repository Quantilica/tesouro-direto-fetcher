"""``list_datasets`` não pode engolir falhas do CKAN (sync saía 0 sem baixar nada)."""

from __future__ import annotations

import logging

import pytest
from quantilica.core.exceptions import CkanError

from tesouro_direto_fetcher import plugin


class _FailingCkan:
    def __init__(self, *_a, **_k) -> None:
        pass

    def package_show(self, _group: str):
        raise CkanError("CKAN request failed for package_show: connection reset")


class _OkCkan:
    def __init__(self, *_a, **_k) -> None:
        pass

    def package_show(self, _group: str):
        return {
            "resources": [
                {"name": "a", "url": "https://x/a.csv", "format": "CSV"},
                {"name": "b", "url": "https://x/b.pdf", "format": "PDF"},
            ]
        }


def test_falha_do_ckan_propaga_e_registra(monkeypatch, caplog) -> None:
    monkeypatch.setattr("quantilica.core.ckan.CkanClient", _FailingCkan)
    with caplog.at_level(logging.ERROR), pytest.raises(CkanError, match="reset"):
        plugin.list_datasets("vendas-do-tesouro-direto")
    assert any("vendas-do-tesouro-direto" in r.getMessage() for r in caplog.records)


def test_lista_apenas_csv(monkeypatch) -> None:
    monkeypatch.setattr("quantilica.core.ckan.CkanClient", _OkCkan)
    entries = plugin.list_datasets("g")
    assert [e["id"] for e in entries] == ["a"]
