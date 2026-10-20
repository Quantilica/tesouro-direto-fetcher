"""Functions to read Tesouro Direto's data files.

This module provides functions to parse raw CSV files downloaded from the
Tesouro Transparente API into clean, analyst-friendly Polars DataFrames.
It handles column renaming (Portuguese to English), type conversion,
and data normalization using the schema defined in `constants.py`.

The DataFrames returned by these functions use standardized column names
defined in the `Column` enum.
"""

from collections.abc import Callable, Iterator
from pathlib import Path

try:
    import polars as pl
except ImportError as exc:
    raise ImportError(
        "tesouro_direto_fetcher.reader requer o extra 'analysis': "
        "uv add 'tesouro-direto-fetcher[analysis]' "
        "--index https://index.quantilica.com/simple/"
    ) from exc

from .constants import (
    NTNB1_CODE,
    RENDA_FIRST_MATURITY_YEAR,
    RENDA_MATURITY_YEAR_STEP,
    AccountStatus,
    Channel,
    Gender,
    TradedLast12Months,
    normalize_bond_type,
)
from .constants import Column as C


def _disambiguate_ntnb1(df: pl.DataFrame) -> pl.DataFrame:
    """Resolve the NTN-B1 code (RendA+ vs EducA+) by maturity date.

    Both Tesouro RendA+ and Tesouro EducA+ appear as "NTN-B1" in some
    datasets; only the final maturity date tells them apart (RendA+ matures
    on Dec 15 of 2049 + 5k). See resolve_bond_type in constants.py.
    """
    if C.MATURITY_DATE.value not in df.columns:
        return df

    maturity = pl.col(C.MATURITY_DATE.value)
    if df.schema[C.MATURITY_DATE.value] == pl.String:
        maturity = maturity.str.to_date("%d/%m/%Y", strict=False)

    year = maturity.dt.year()
    is_renda = (
        (maturity.dt.month() == 12)
        & (maturity.dt.day() == 15)
        & (year >= RENDA_FIRST_MATURITY_YEAR)
        & ((year - RENDA_FIRST_MATURITY_YEAR) % RENDA_MATURITY_YEAR_STEP == 0)
    )

    return df.with_columns(
        pl.when(
            pl.col(C.BOND_TYPE.value).str.strip_chars().str.to_uppercase() == NTNB1_CODE
        )
        .then(
            pl.when(is_renda.fill_null(False))
            .then(pl.lit("Tesouro RendA+"))
            .otherwise(pl.lit("Tesouro EducA+"))
        )
        .otherwise(pl.col(C.BOND_TYPE.value))
        .alias(C.BOND_TYPE.value)
    )


def _read_and_process_csv(
    filepath: Path,
    column_mapping: dict[str, str],
    date_columns: list[str] | None = None,
    dtype_mapping: dict[str, str] | None = None,
    post_process_func: Callable[[pl.DataFrame], pl.DataFrame] | None = None,
    chunksize: int | None = None,
) -> pl.DataFrame | Iterator[pl.DataFrame]:
    """Generic function to read and process a CSV file."""

    def _process(df: pl.DataFrame) -> pl.DataFrame:
        existing_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(existing_mapping)
        if C.BOND_TYPE.value in df.columns:
            df = df.with_columns(
                pl.col(C.BOND_TYPE.value).map_elements(
                    normalize_bond_type, return_dtype=pl.String
                )
            )
            df = _disambiguate_ntnb1(df)
        if dtype_mapping:
            # Convert dtype string to Polars casting
            for col, dtype in dtype_mapping.items():
                if col in df.columns:
                    if dtype == "category":
                        df = df.with_columns(pl.col(col).cast(pl.Categorical))
        if post_process_func:
            df = post_process_func(df)
        return df

    if chunksize is None:
        # Full read
        data = pl.read_csv(
            filepath,
            separator=";",
            decimal_comma=True,
        )
        return _process(data)
    else:
        # Batched reading — use `scan_csv().collect_batches()` to avoid deprecated API
        lf = pl.scan_csv(
            filepath,
            separator=";",
            decimal_comma=True,
        )
        batches = lf.collect_batches(chunk_size=chunksize)

        def _batch_generator() -> Iterator[pl.DataFrame]:
            # `collect_batches()` returns an iterator of DataFrames (streamed chunks).
            for batch in batches:
                yield _process(batch)

        return _batch_generator()


def read_prices(
    filepath: Path, chunksize: int | None = None
) -> pl.DataFrame | Iterator[pl.DataFrame]:
    """Read bond prices and rates (Taxas e Preços dos Títulos).

    Args:
        filepath (Path): Path to the CSV file.
        chunksize (int | None, optional): Number of lines to read from the CSV file at a
            time. Defaults to None.

    Returns:
        pl.DataFrame | Iterator[pl.DataFrame]: DataFrame or an iterator of DataFrames.
    """
    column_mapping = {
        "Data Base": C.REFERENCE_DATE.value,
        "Tipo Titulo": C.BOND_TYPE.value,
        "Data Vencimento": C.MATURITY_DATE.value,
        "Taxa Compra Manha": C.BUY_YIELD.value,
        "Taxa Venda Manha": C.SELL_YIELD.value,
        "PU Compra Manha": C.BUY_PRICE.value,
        "PU Venda Manha": C.SELL_PRICE.value,
        "PU Base Manha": C.BASE_PRICE.value,
    }

    def post_process(df: pl.DataFrame) -> pl.DataFrame:
        # Parse dates with day-first format
        return df.with_columns(
            [
                pl.col(C.REFERENCE_DATE.value).str.to_date("%d/%m/%Y"),
                pl.col(C.MATURITY_DATE.value).str.to_date("%d/%m/%Y"),
            ]
        )

    return _read_and_process_csv(
        filepath,
        column_mapping,
        post_process_func=post_process,
        chunksize=chunksize,
    )


def read_stock(
    filepath: Path, chunksize: int | None = None
) -> pl.DataFrame | Iterator[pl.DataFrame]:
    """Read bond stock (Estoque).

    Args:
        filepath (Path): Path to the CSV file.
        chunksize (int | None, optional): Number of lines to read from the CSV file at a
            time. Defaults to None.

    Returns:
        pl.DataFrame | Iterator[pl.DataFrame]: DataFrame or an iterator of DataFrames.
    """
    column_mapping = {
        "Tipo Titulo": C.BOND_TYPE.value,
        "Vencimento do Titulo": C.MATURITY_DATE.value,
        "Mes Estoque": C.STOCK_MONTH.value,
        "PU": C.UNIT_PRICE.value,
        "Quantidade": C.QUANTITY.value,
        "Valor Estoque": C.STOCK_VALUE.value,
    }

    def post_process(df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns(
            [
                pl.col(C.MATURITY_DATE.value).str.to_date("%d/%m/%Y"),
                pl.col(C.STOCK_MONTH.value).str.to_date("%m/%Y"),
            ]
        )

    return _read_and_process_csv(
        filepath,
        column_mapping,
        post_process_func=post_process,
        chunksize=chunksize,
    )


def read_investors(
    filepath: Path, chunksize: int | None = None
) -> pl.DataFrame | Iterator[pl.DataFrame]:
    """Read investors data (Investidores).

    Args:
        filepath (Path): Path to the CSV file.
        chunksize (int | None, optional): Number of lines to read from the CSV file at a
            time. Defaults to None.

    Returns:
        pl.DataFrame | Iterator[pl.DataFrame]: DataFrame or an iterator of DataFrames.
    """
    column_mapping = {
        "Codigo do Investidor": C.INVESTOR_ID.value,
        "Data de Adesao": C.JOIN_DATE.value,
        "Estado Civil": C.MARITAL_STATUS.value,
        "Genero": C.GENDER.value,
        "Profissao": C.PROFESSION.value,
        "Idade": C.AGE.value,
        "UF do Investidor": C.STATE.value,
        "Cidade do Investidor": C.CITY.value,
        "Pais do Investidor": C.COUNTRY.value,
        "Situacao da Conta": C.ACCOUNT_STATUS.value,
        "Operou 12 Meses": C.TRADED_LAST_12_MONTHS.value,
    }
    dtype_mapping = {
        C.MARITAL_STATUS.value: "category",
        C.PROFESSION.value: "category",
        C.STATE.value: "category",
        C.CITY.value: "category",
        C.COUNTRY.value: "category",
    }

    def post_process(df: pl.DataFrame) -> pl.DataFrame:
        # Parse date
        df = df.with_columns(pl.col(C.JOIN_DATE.value).str.to_date("%d/%m/%Y"))
        # Map enum values and cast to categorical
        gender_map = {e.value: e.value for e in Gender}
        status_map = {e.value: e.value for e in AccountStatus}
        traded_map = {e.value: e.value for e in TradedLast12Months}

        df = df.with_columns(
            [
                pl.col(C.GENDER.value).replace(gender_map).cast(pl.Categorical),
                pl.col(C.ACCOUNT_STATUS.value).replace(status_map).cast(pl.Categorical),
                pl.col(C.TRADED_LAST_12_MONTHS.value)
                .replace(traded_map)
                .cast(pl.Categorical),
            ]
        )
        return df

    return _read_and_process_csv(
        filepath,
        column_mapping,
        dtype_mapping=dtype_mapping,
        post_process_func=post_process,
        chunksize=chunksize,
    )


def read_operations(
    filepath: Path, chunksize: int | None = None
) -> pl.DataFrame | Iterator[pl.DataFrame]:
    """Read operations data (Operações).

    Args:
        filepath (Path): Path to the CSV file.
        chunksize (int | None, optional): Number of lines to read from the CSV file at a
            time. Defaults to None.

    Returns:
        pl.DataFrame | Iterator[pl.DataFrame]: DataFrame or an iterator of DataFrames.
    """
    column_mapping = {
        "Codigo do Investidor": C.INVESTOR_ID.value,
        "Data da Operacao": C.OPERATION_DATE.value,
        "Tipo Titulo": C.BOND_TYPE.value,
        "Vencimento do Titulo": C.MATURITY_DATE.value,
        "Quantidade": C.QUANTITY.value,
        "Valor do Titulo": C.BOND_VALUE.value,
        "Valor da Operacao": C.OPERATION_VALUE.value,
        "Tipo da Operacao": C.OPERATION_TYPE.value,
        "Canal da Operacao": C.CHANNEL.value,
    }

    def post_process(df: pl.DataFrame) -> pl.DataFrame:
        # Parse dates
        df = df.with_columns(
            [
                pl.col(C.OPERATION_DATE.value).str.to_date("%d/%m/%Y"),
                pl.col(C.MATURITY_DATE.value).str.to_date("%d/%m/%Y"),
            ]
        )
        # Map enum values and cast to categorical
        channel_map = {e.value: e.value for e in Channel}
        df = df.with_columns(
            [
                pl.col(C.CHANNEL.value).replace(channel_map).cast(pl.Categorical),
                pl.col(C.BOND_TYPE.value).cast(pl.Categorical),
            ]
        )
        return df

    return _read_and_process_csv(
        filepath,
        column_mapping,
        post_process_func=post_process,
        chunksize=chunksize,
    )


def read_sales(
    filepath: Path, chunksize: int | None = None
) -> pl.DataFrame | Iterator[pl.DataFrame]:
    """Read sales data (Vendas).

    Args:
        filepath (Path): Path to the CSV file.
        chunksize (int | None, optional): Number of lines to read from the CSV file at a
            time. Defaults to None.

    Returns:
        pl.DataFrame | Iterator[pl.DataFrame]: DataFrame or an iterator of DataFrames.
    """
    column_mapping = {
        "Tipo Titulo": C.BOND_TYPE.value,
        "Vencimento do Titulo": C.MATURITY_DATE.value,
        "Data Venda": C.SALE_DATE.value,
        "Data de Liquidacao da Venda": C.SALE_DATE.value,
        "PU": C.UNIT_PRICE.value,
        "Quantidade": C.QUANTITY.value,
        "Valor": C.VALUE.value,
    }

    def post_process(df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns(
            [
                pl.col(C.MATURITY_DATE.value).str.to_date("%d/%m/%Y"),
                pl.col(C.SALE_DATE.value).str.to_date("%d/%m/%Y"),
            ]
        )

    return _read_and_process_csv(
        filepath,
        column_mapping,
        post_process_func=post_process,
        chunksize=chunksize,
    )


def read_buybacks(
    filepath: Path, chunksize: int | None = None
) -> pl.DataFrame | Iterator[pl.DataFrame]:
    """Read buybacks data (Resgates).

    Args:
        filepath (Path): Path to the CSV file.
        chunksize (int | None, optional): Number of lines to read from the CSV file at a
            time. Defaults to None.

    Returns:
        pl.DataFrame | Iterator[pl.DataFrame]: DataFrame or an iterator of DataFrames.
    """
    column_mapping = {
        "Tipo Titulo": C.BOND_TYPE.value,
        "Vencimento do Titulo": C.MATURITY_DATE.value,
        "Data Resgate": C.BUYBACK_DATE.value,
        "Quantidade": C.QUANTITY.value,
        "Valor": C.VALUE.value,
    }

    def post_process(df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns(
            [
                pl.col(C.MATURITY_DATE.value).str.to_date("%d/%m/%Y"),
                pl.col(C.BUYBACK_DATE.value).str.to_date("%d/%m/%Y"),
            ]
        )

    return _read_and_process_csv(
        filepath,
        column_mapping,
        post_process_func=post_process,
        chunksize=chunksize,
    )


def read_maturities(
    filepath: Path, chunksize: int | None = None
) -> pl.DataFrame | Iterator[pl.DataFrame]:
    """Read maturities data (Vencimentos).

    Args:
        filepath (Path): Path to the CSV file.
        chunksize (int | None, optional): Number of lines to read from the CSV file at a
            time. Defaults to None.

    Returns:
        pl.DataFrame | Iterator[pl.DataFrame]: DataFrame or an iterator of DataFrames.
    """
    column_mapping = {
        "Tipo Titulo": C.BOND_TYPE.value,
        "Vencimento do Titulo": C.MATURITY_DATE.value,
        "Data Resgate": C.BUYBACK_DATE.value,
        "PU": C.UNIT_PRICE.value,
        "Quantidade": C.QUANTITY.value,
        "Valor": C.VALUE.value,
    }

    def post_process(df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns(
            [
                pl.col(C.MATURITY_DATE.value).str.to_date("%d/%m/%Y"),
                pl.col(C.BUYBACK_DATE.value).str.to_date("%d/%m/%Y"),
            ]
        )

    return _read_and_process_csv(
        filepath,
        column_mapping,
        post_process_func=post_process,
        chunksize=chunksize,
    )


def read_interest_coupons(
    filepath: Path, chunksize: int | None = None
) -> pl.DataFrame | Iterator[pl.DataFrame]:
    """Read interest coupons data (Pagamento de Cupom de Juros).

    Parses the history of interest coupon payments.
    This file shares the same structure as the maturities file.

    Args:
        filepath: Path to the CSV file.
        chunksize: Number of lines to read from the CSV file at a time.

    Returns:
        pl.DataFrame or Iterator[pl.DataFrame]: DataFrame with columns similar to
            `read_maturities`.
    """
    return read_maturities(filepath, chunksize=chunksize)
