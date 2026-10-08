"""Import guard da CLI standalone do tesouro-direto-fetcher."""

from __future__ import annotations

import importlib
import sys
import types

import pytest

import tesouro_direto_fetcher.cli as cli_module

_PLUGIN_KEY = "tesouro_direto_fetcher.plugin"
_PKG = "tesouro_direto_fetcher"


def _pkg_modules() -> dict[str, object]:
    """Snapshot dos módulos do pacote presentes em sys.modules."""
    return {
        name: mod
        for name, mod in sys.modules.items()
        if name == _PKG or name.startswith(_PKG + ".")
    }


@pytest.fixture
def _no_plugin():
    """Simular host ausente (typer bloqueado) e restaurar os módulos ao final."""
    saved_typer = sys.modules.get("typer")
    had_plugin = _PLUGIN_KEY in sys.modules
    saved_plugin = sys.modules.get(_PLUGIN_KEY)
    saved_pkg = _pkg_modules()
    sys.modules["typer"] = None
    sys.modules.pop(_PLUGIN_KEY, None)  # forcar reimport do plugin
    mod = importlib.reload(cli_module)
    yield mod
    if saved_typer is None:
        sys.modules.pop("typer", None)
    else:
        sys.modules["typer"] = saved_typer
    if had_plugin:
        sys.modules[_PLUGIN_KEY] = saved_plugin
    elif _PLUGIN_KEY in sys.modules:
        del sys.modules[_PLUGIN_KEY]
    importlib.reload(cli_module)
    sys.modules.update(saved_pkg)
    if _PKG in saved_pkg:
        importlib.reload(sys.modules[_PKG])


def test_import_cli_sem_plugin_nao_levanta_erro(_no_plugin) -> None:
    """Importar cli sem o plugin disponível não levanta ModuleNotFoundError."""
    assert _no_plugin.app is None
    assert _no_plugin._PLUGIN_ERROR is not None


def test_main_sem_plugin_sai_1_e_orienta_install(_no_plugin, capsys) -> None:
    """main([]) sai com SystemExit(1) e orienta 'quantilica install td'."""
    with pytest.raises(SystemExit) as exc_info:
        _no_plugin.main([])
    assert exc_info.value.code == 1
    stderr = capsys.readouterr().err
    assert "Erro: CLI requer 'typer' e 'rich' (via quantilica-cli)." in stderr
    assert 'Instale via "quantilica install td".' in stderr
    assert "Detalhe:" in stderr


def test_importerror_interno_do_plugin_propaga() -> None:
    """ImportError de modulo fora do host (bug interno) nao vira exit 1: propaga."""
    saved = sys.modules.get(_PLUGIN_KEY)
    stub = types.ModuleType(_PLUGIN_KEY)

    def __getattr__(name):
        raise ModuleNotFoundError("No module named 'outro_modulo'", name="outro_modulo")

    stub.__getattr__ = __getattr__
    sys.modules[_PLUGIN_KEY] = stub
    try:
        with pytest.raises(ModuleNotFoundError):
            importlib.reload(cli_module)
    finally:
        if saved is None:
            sys.modules.pop(_PLUGIN_KEY, None)
        else:
            sys.modules[_PLUGIN_KEY] = saved
        importlib.reload(cli_module)
