"""Command-line interface for tesouro-direto-fetcher."""

from __future__ import annotations

import sys

from quantilica.core.logging import configure_cli_logging

_HOST_MODULES = {"typer", "rich", "quantilica"}

try:
    from .plugin import app
except ImportError as exc:  # host (typer/rich/quantilica-cli) ausente
    if (exc.name or "").split(".")[0] not in _HOST_MODULES:
        raise
    app = None
    _PLUGIN_ERROR = exc
else:
    _PLUGIN_ERROR = None


def main(argv: list[str] | None = None) -> None:
    """Execute the command-line interface.

    Args:
        argv: Optional list of command-line arguments; None uses sys.argv.

    Raises:
        SystemExit: Always — 0 on success (via Typer) or 130 on Ctrl+C; 1 when
            the host (typer/rich/quantilica-cli) is not installed.
    """
    if app is None:
        print(
            "Erro: CLI requer 'typer' e 'rich' (via quantilica-cli). "
            'Instale via "quantilica install tesouro-direto". '
            f"Detalhe: {_PLUGIN_ERROR}",
            file=sys.stderr,
        )
        raise SystemExit(1)
    # We still configure basic cli logging, but the new UI setup in
    # plugin will handle rich logging.
    configure_cli_logging(verbose=False)

    # Typer apps usually read sys.argv by themselves if argv is not provided
    # However, if argv is provided (e.g. in tests), we need to handle it.
    if argv is None:
        argv = sys.argv[1:]

    try:
        # typer apps can be called directly
        app(argv)
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
