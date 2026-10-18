from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("tesouro-direto-fetcher")
except PackageNotFoundError:
    __version__ = "0.0.0"

from .constants import (  # noqa: E402
    AccountStatus,
    BondType,
    Channel,
    Column,
    Gender,
    MaritalStatus,
    OperationType,
    TradedLast12Months,
)

# Optional imports - only available if analysis extras are installed
try:
    from . import plot, reader  # noqa: E402

    _HAS_ANALYSIS = True
except ImportError:
    _HAS_ANALYSIS = False
    plot = None  # type: ignore
    reader = None  # type: ignore

__all__ = [
    "__version__",
    "Column",
    "BondType",
    "OperationType",
    "Channel",
    "Gender",
    "MaritalStatus",
    "AccountStatus",
    "TradedLast12Months",
]

if _HAS_ANALYSIS:
    __all__.extend(["plot", "reader"])
