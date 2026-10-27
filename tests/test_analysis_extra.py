"""Tests for tesouro_direto_fetcher analysis-extra import guard."""

import importlib
import sys

import pytest

MODULES = [
    "tesouro_direto_fetcher.reader",
    "tesouro_direto_fetcher.analytics",
    "tesouro_direto_fetcher.fast_returns",
    "tesouro_direto_fetcher.plot",
    "tesouro_direto_fetcher.converter",
    "tesouro_direto_fetcher.lake",
]

BLOCKED = [
    "polars",
    "altair",
    "quantilica.analytics",
    "quantilica.analytics.writer",
    "quantilica.analytics.lake",
]


def test_analysis_extra_mensagem_acionavel():
    salvos = {name: sys.modules.get(name) for name in BLOCKED}
    try:
        for module_name in MODULES:
            for name in BLOCKED:
                sys.modules[name] = None
            sys.modules.pop(module_name, None)
            try:
                with pytest.raises(ImportError, match="requer o extra 'analysis'"):
                    importlib.import_module(module_name)
            finally:
                sys.modules.pop(module_name, None)
    finally:
        for name, mod in salvos.items():
            if mod is not None:
                sys.modules[name] = mod
            else:
                sys.modules.pop(name, None)
        for module_name in MODULES:
            sys.modules.pop(module_name, None)
        if salvos["polars"] is not None:
            for module_name in MODULES:
                importlib.import_module(module_name)
