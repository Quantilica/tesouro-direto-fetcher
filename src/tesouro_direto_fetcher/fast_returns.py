"""Vectorized return calculations for many investors at once.

These functions reproduce the per-investor calculations in ``analytics``
(``calculate_operations_returns`` and ``calculate_portfolio_monthly_returns``)
as whole-DataFrame Polars pipelines, so a single call processes every investor
in the input. Polars parallelizes the work across all CPU cores, which makes
this path orders of magnitude faster than looping investor by investor.

Semantics follow the legacy functions, including their handling of degenerate
data: position quantities are clamped at zero after every operation (sells
exceeding the tracked holdings discard the negative residual), and FIFO
consumes sells in input-row order, exactly like the legacy loop. The only
expected differences are floating-point dust: cumulative sums accumulate
rounding differently from sequential subtraction, so lots whose quantity is
smaller than 1e-9 are dropped here while the legacy code may emit or omit
them depending on rounding.
"""

from datetime import date

try:
    import polars as pl
except ImportError as exc:
    raise ImportError(
        "tesouro_direto_fetcher.fast_returns requer o extra 'analysis': "
        "uv add 'tesouro-direto-fetcher[analysis]' "
        "--index https://index.quantilica.com/simple/"
    ) from exc

from .constants import Column as C
from .constants import OperationType

_INV = C.INVESTOR_ID.value
_BT = C.BOND_TYPE.value
_MAT = C.MATURITY_DATE.value
_OP_DATE = C.OPERATION_DATE.value
_OP_TYPE = C.OPERATION_TYPE.value
_QTY = C.QUANTITY.value
_OP_VALUE = C.OPERATION_VALUE.value
_BOND_VALUE = C.BOND_VALUE.value
_REF_DATE = C.REFERENCE_DATE.value
_SELL_PRICE = C.SELL_PRICE.value
_CPN_DATE = C.BUYBACK_DATE.value
_UNIT_PRICE = C.UNIT_PRICE.value

_BUY = OperationType.BUY.value
_SELL = OperationType.SELL.value


def _normalize_ops(operations: pl.DataFrame) -> pl.DataFrame:
    """Cast key columns to join-friendly dtypes and add helper columns."""
    return (
        operations.with_row_index("_row")
        .with_columns(
            pl.col(_BT).cast(pl.Utf8),
            pl.col(_MAT).cast(pl.Date).alias("_mat"),
            pl.col(_OP_DATE).cast(pl.Date).alias("_op_date"),
            pl.col(_QTY).cast(pl.Float64).fill_null(0.0).alias("_qty"),
            pl.col(_OP_VALUE).cast(pl.Float64).fill_null(0.0).alias("_value"),
        )
        .with_columns(pl.col("_op_date").dt.truncate("1mo").alias("_month"))
    )


def _normalize_prices(prices: pl.DataFrame) -> pl.DataFrame:
    return prices.with_columns(
        pl.col(_BT).cast(pl.Utf8),
        pl.col(_MAT).cast(pl.Date).alias("_mat"),
        pl.col(_REF_DATE).cast(pl.Date).alias("_ref"),
        pl.col(_SELL_PRICE).cast(pl.Float64).alias("_price"),
    )


def _normalize_coupons(coupons: pl.DataFrame) -> pl.DataFrame:
    return coupons.with_columns(
        pl.col(_BT).cast(pl.Utf8),
        pl.col(_MAT).cast(pl.Date).alias("_mat"),
        pl.col(_CPN_DATE).cast(pl.Date).alias("_cpn_date"),
        pl.col(_UNIT_PRICE).cast(pl.Float64).fill_null(0.0).alias("_cpn_unit"),
    )


def _monthly_price_grid(
    prices: pl.DataFrame, needed_keys: pl.DataFrame, end_month: date
) -> pl.DataFrame:
    """Month-start and month-end prices per (bond_type, maturity, month).

    For every (bond_type, maturity) in ``needed_keys``, builds a dense month
    range from the first priced month up to ``end_month`` with:

    - ``_p_end``: last price with reference date <= end of month (carried
      forward across months without prices);
    - ``_p_start``: last price with reference date <= first day of month
      (the day-1 price when it exists, otherwise the previous month's close).
    """
    pr = prices.join(needed_keys, on=[_BT, "_mat"], how="semi").sort(
        [_BT, "_mat", "_ref"]
    )
    if pr.height == 0:
        return pl.DataFrame(
            schema={
                _BT: pl.Utf8,
                "_mat": pl.Date,
                "_month": pl.Date,
                "_p_end": pl.Float64,
                "_p_start": pl.Float64,
            }
        )

    pr = pr.with_columns(pl.col("_ref").dt.truncate("1mo").alias("_month"))
    month_close = pr.group_by([_BT, "_mat", "_month"], maintain_order=True).agg(
        pl.col("_price").last().alias("_p_close")
    )
    day1 = (
        pr.filter(pl.col("_ref") == pl.col("_month"))
        .group_by([_BT, "_mat", "_month"], maintain_order=True)
        .agg(pl.col("_price").last().alias("_p_day1"))
    )

    grid = (
        month_close.group_by([_BT, "_mat"])
        .agg(pl.col("_month").min().alias("_first"))
        .with_columns(
            pl.date_ranges(pl.col("_first"), pl.lit(end_month), interval="1mo").alias(
                "_month"
            )
        )
        .explode("_month")
        .drop("_first")
        .join(month_close, on=[_BT, "_mat", "_month"], how="left")
        .sort([_BT, "_mat", "_month"])
        .with_columns(
            pl.col("_p_close").forward_fill().over([_BT, "_mat"]).alias("_p_end")
        )
        .join(day1, on=[_BT, "_mat", "_month"], how="left")
        .with_columns(
            pl.coalesce(
                pl.col("_p_day1"),
                pl.col("_p_end").shift(1).over([_BT, "_mat"]),
            ).alias("_p_start")
        )
    )
    return grid.select([_BT, "_mat", "_month", "_p_end", "_p_start"])


_MONTHLY_SCHEMA: dict[str, pl.DataType] = {
    "month": pl.Date,
    "monthly_return": pl.Float64,
    "cumulative_return": pl.Float64,
    "portfolio_value": pl.Float64,
    "net_cash_flow": pl.Float64,
}


def calculate_monthly_returns_bulk(
    operations: pl.DataFrame,
    prices: pl.DataFrame,
    coupons: pl.DataFrame | None = None,
    by_bond_type: bool = False,
) -> pl.DataFrame:
    """Monthly Modified Dietz returns for every investor in ``operations``.

    Vectorized equivalent of calling
    ``analytics.calculate_portfolio_monthly_returns`` once per investor (or
    once per investor and bond type when ``by_bond_type`` is True).

    Args:
        operations (pl.DataFrame): Operations DataFrame.
        prices (pl.DataFrame): Prices DataFrame.
        coupons (pl.DataFrame | None, optional): Optional coupons DataFrame. Defaults to
            None.
        by_bond_type (bool, optional): Whether to group returns by bond type. Defaults
            to False.

    Returns:
        pl.DataFrame: A DataFrame with columns ``investor_id`` (+ ``bond_type``),
        ``month``, ``monthly_return``, ``cumulative_return``, ``portfolio_value``
        and ``net_cash_flow``, sorted by group and month.
    """
    gkeys = [_INV, _BT] if by_bond_type else [_INV]
    out_schema: dict[str, pl.DataType] = {
        _INV: operations.schema.get(_INV, pl.Int64),
        **({_BT: pl.Utf8} if by_bond_type else {}),
        **_MONTHLY_SCHEMA,
    }
    if operations.height == 0 or prices.height == 0:
        return pl.DataFrame(schema=out_schema)

    ops = _normalize_ops(operations)
    pos_keys = [_INV, _BT, "_mat"]

    # Month range per group spans all operation types (legacy behavior)
    ranges = ops.group_by(gkeys).agg(
        pl.col("_month").min().alias("_g_start"),
        pl.col("_month").max().alias("_g_end"),
    )

    # Cash flows and position deltas only consider buys and sells
    fl = ops.filter(pl.col(_OP_TYPE).is_in([_BUY, _SELL])).with_columns(
        pl.when(pl.col(_OP_TYPE) == _BUY)
        .then(pl.col("_qty"))
        .otherwise(-pl.col("_qty").abs())
        .alias("_dqty"),
        pl.when(pl.col(_OP_TYPE) == _BUY)
        .then(pl.col("_value"))
        .otherwise(-pl.col("_value"))
        .alias("_cf"),
    )
    flows = fl.group_by(gkeys + ["_month"]).agg(
        pl.col("_cf").sum().alias("_net_cf_ops")
    )
    # Clamped running position after every operation: the legacy loop drops a
    # position the moment a sell takes it to <= 0 (discarding the negative
    # residual) and rebuilds it on later buys. That recurrence
    # ``pos = max(0, pos + delta)`` equals ``S - min(0, running_min(S))`` over
    # the cumulative sum S, evaluated op by op in input-row order within each
    # month (the order the legacy month loop iterates).
    month_pos = (
        fl.sort(pos_keys + ["_month", "_row"])
        .with_columns(pl.col("_dqty").cum_sum().over(pos_keys).alias("_cum"))
        .with_columns(
            (
                pl.col("_cum")
                - pl.min_horizontal(pl.col("_cum").cum_min().over(pos_keys), 0.0)
            ).alias("_q_op")
        )
        .group_by(pos_keys + ["_month"], maintain_order=True)
        .agg(pl.col("_q_op").last().alias("_q_month"))
    )

    # Dense (position key x month) grid over each group's month range
    dense = (
        month_pos.select(pos_keys)
        .unique()
        .join(ranges, on=gkeys)
        .with_columns(
            pl.date_ranges(pl.col("_g_start"), pl.col("_g_end"), interval="1mo").alias(
                "_month"
            )
        )
        .explode("_month")
        .drop(["_g_start", "_g_end"])
        .join(month_pos, on=pos_keys + ["_month"], how="left")
        .sort(pos_keys + ["_month"])
        .with_columns(
            pl.col("_q_month")
            .forward_fill()
            .over(pos_keys)
            .fill_null(0.0)
            .alias("_q_end")
        )
        .with_columns(
            pl.col("_q_end").shift(1).fill_null(0.0).over(pos_keys).alias("_q_begin")
        )
    )

    if dense.height == 0:
        # Only deposit/withdrawal operations: every month is a zero row
        return (
            ranges.with_columns(
                pl.date_ranges(
                    pl.col("_g_start"), pl.col("_g_end"), interval="1mo"
                ).alias("month")
            )
            .explode("month")
            .drop(["_g_start", "_g_end"])
            .with_columns(
                pl.lit(0.0).alias("monthly_return"),
                pl.lit(0.0).alias("cumulative_return"),
                pl.lit(0.0).alias("portfolio_value"),
                pl.lit(0.0).alias("net_cash_flow"),
            )
            .sort(gkeys + ["month"])
            .select(list(out_schema.keys()))
        )

    end_month: date = dense["_month"].max()  # type: ignore[assignment]
    price_grid = _monthly_price_grid(
        _normalize_prices(prices), dense.select([_BT, "_mat"]).unique(), end_month
    )
    dense = dense.join(price_grid, on=[_BT, "_mat", "_month"], how="left")

    if coupons is not None and coupons.height > 0:
        cpn = (
            _normalize_coupons(coupons)
            .with_columns(pl.col("_cpn_date").dt.truncate("1mo").alias("_month"))
            .group_by([_BT, "_mat", "_month"])
            .agg(pl.col("_cpn_unit").sum())
        )
        dense = dense.join(cpn, on=[_BT, "_mat", "_month"], how="left").with_columns(
            pl.col("_cpn_unit").fill_null(0.0)
        )
    else:
        dense = dense.with_columns(pl.lit(0.0).alias("_cpn_unit"))

    # Null prices mean "no price known yet": the position adds no value
    # (sum() skips nulls), matching the legacy lookup returning None.
    agg = dense.group_by(gkeys + ["_month"]).agg(
        (pl.col("_q_begin") * pl.col("_p_start")).sum().alias("_bmv"),
        (pl.col("_q_end") * pl.col("_p_end")).sum().alias("_emv"),
        (pl.col("_q_end") * pl.col("_cpn_unit")).sum().alias("_coupon"),
    )

    result = (
        ranges.with_columns(
            pl.date_ranges(pl.col("_g_start"), pl.col("_g_end"), interval="1mo").alias(
                "_month"
            )
        )
        .explode("_month")
        .drop(["_g_start", "_g_end"])
        .join(agg, on=gkeys + ["_month"], how="left")
        .join(flows, on=gkeys + ["_month"], how="left")
        .with_columns(pl.col("_bmv", "_emv", "_coupon", "_net_cf_ops").fill_null(0.0))
        .with_columns(
            (pl.col("_net_cf_ops") - pl.col("_coupon")).alias("net_cash_flow")
        )
        .with_columns((pl.col("_bmv") + pl.col("net_cash_flow") / 2.0).alias("_denom"))
        .with_columns(
            pl.when(pl.col("_denom") > 0.01)
            .then(
                (pl.col("_emv") - pl.col("_bmv") - pl.col("net_cash_flow"))
                / pl.col("_denom")
                * 100.0
            )
            .otherwise(0.0)
            .alias("monthly_return")
        )
        .sort(gkeys + ["_month"])
        .with_columns(
            (
                ((pl.col("monthly_return") / 100.0 + 1.0).cum_prod().over(gkeys) - 1.0)
                * 100.0
            ).alias("cumulative_return")
        )
        .rename({"_month": "month", "_emv": "portfolio_value"})
    )

    return result.select(
        gkeys
        + [
            "month",
            "monthly_return",
            "cumulative_return",
            "portfolio_value",
            "net_cash_flow",
        ]
    )


def calculate_lots_bulk(
    operations: pl.DataFrame,
    prices: pl.DataFrame,
    coupons: pl.DataFrame | None = None,
    current_date: date | None = None,
) -> pl.DataFrame:
    """FIFO lot-level returns for every investor in ``operations``.

    Vectorized equivalent of calling ``analytics.calculate_operations_returns``
    once per investor. Sells are matched to buys with FIFO by aligning the
    cumulative-quantity intervals of buys and sells within each
    (investor, bond_type, maturity) group: every overlap of a buy interval
    with a sell interval is a closed lot, and the unmatched tail of each buy
    interval is an open lot.

    Args:
        operations (pl.DataFrame): Operations DataFrame.
        prices (pl.DataFrame): Prices DataFrame.
        coupons (pl.DataFrame | None, optional): Optional coupons DataFrame. Defaults to
            None.
        current_date (date | None, optional): Date to calculate returns up to. Defaults
            to None.

    Returns:
        pl.DataFrame: One row per lot with the same metric columns as the legacy
        function, plus ``investor_id``.
    """
    if operations.height == 0:
        return pl.DataFrame()
    if _BOND_VALUE in operations.columns:
        operations = operations.filter(pl.col(_BOND_VALUE) != 0)
    if operations.height == 0:
        return pl.DataFrame()

    if current_date is None:
        current_date = date.today()

    ops = _normalize_ops(operations)
    keys = [_INV, _BT, "_mat"]

    buys = (
        ops.filter(pl.col(_OP_TYPE) == _BUY)
        .with_columns(
            pl.when(pl.col("_qty") > 0)
            .then(pl.col("_value") / pl.col("_qty"))
            .otherwise(0.0)
            .alias("_unit_buy")
        )
        .sort(keys + ["_op_date", "_row"])
        .with_columns(pl.col("_qty").cum_sum().over(keys).alias("_b1"))
        .with_columns((pl.col("_b1") - pl.col("_qty")).alias("_b0"))
    )
    if buys.height == 0:
        return pl.DataFrame()

    # Sells consume the FIFO queue in input-row order (legacy behavior)
    sells = (
        ops.filter(pl.col(_OP_TYPE) == _SELL)
        .with_columns(
            pl.col("_qty").abs().alias("_sqty"),
            pl.col("_value").abs().alias("_sval"),
        )
        .filter(pl.col("_sqty") > 0)
        .with_columns((pl.col("_sval") / pl.col("_sqty")).alias("_unit_sell"))
        .sort(keys + ["_row"])
        .with_columns(pl.col("_sqty").cum_sum().over(keys).alias("_s1"))
        .with_columns((pl.col("_s1") - pl.col("_sqty")).alias("_s0"))
    )

    total_sold = sells.group_by(keys).agg(pl.col("_s1").max().alias("_total_s"))

    # --- Closed lots: overlaps between buy and sell cumulative intervals.
    # Buy and sell intervals each tile [0, total] contiguously, so the union
    # of their boundaries splits the axis into segments that belong to exactly
    # one buy and one sell — each such segment is one closed lot.
    closed = pl.DataFrame()
    if sells.height > 0:
        breakpoints = (
            pl.concat(
                [
                    buys.select(keys + [pl.col("_b0").alias("_pt")]),
                    buys.select(keys + [pl.col("_b1").alias("_pt")]),
                    sells.select(keys + [pl.col("_s0").alias("_pt")]),
                    sells.select(keys + [pl.col("_s1").alias("_pt")]),
                ]
            )
            .unique()
            .sort(keys + ["_pt"])
        )
        segments = (
            breakpoints.with_columns(pl.col("_pt").shift(-1).over(keys).alias("_hi"))
            .rename({"_pt": "_lo"})
            .drop_nulls("_hi")
            # > 1e-9 also drops floating-point dust segments created by
            # cumulative sums of buy and sell quantities that should coincide
            .filter((pl.col("_hi") - pl.col("_lo")) > 1e-9)
            .join(
                buys.group_by(keys).agg(pl.col("_b1").max().alias("_total_b")),
                on=keys,
            )
            .join(total_sold, on=keys, how="left")
            .with_columns(pl.col("_total_s").fill_null(0.0))
            .filter(
                pl.col("_hi")
                <= pl.min_horizontal(pl.col("_total_b"), pl.col("_total_s"))
            )
            .sort(keys + ["_lo"])
        )
        closed = segments.join_asof(
            buys.select(
                keys
                + [
                    "_b0",
                    pl.col("_op_date").alias("_buy_date"),
                    pl.col("_unit_buy"),
                    pl.col(_MAT).alias("_mat_orig"),
                ]
            ).sort(keys + ["_b0"]),
            left_on="_lo",
            right_on="_b0",
            by=keys,
            strategy="backward",
            check_sortedness=False,
        ).join_asof(
            sells.select(
                keys
                + [
                    "_s0",
                    pl.col("_op_date").alias("_sell_date"),
                    pl.col("_unit_sell"),
                ]
            ).sort(keys + ["_s0"]),
            left_on="_lo",
            right_on="_s0",
            by=keys,
            strategy="backward",
            check_sortedness=False,
        )
        closed = closed.select(
            keys
            + [
                pl.col("_mat_orig"),
                pl.col("_buy_date"),
                (pl.col("_hi") - pl.col("_lo")).alias("_lot_qty"),
                (pl.col("_unit_buy") * (pl.col("_hi") - pl.col("_lo"))).alias(
                    "_lot_value"
                ),
                pl.col("_sell_date"),
                (pl.col("_unit_sell") * (pl.col("_hi") - pl.col("_lo"))).alias(
                    "sell_value"
                ),
                (pl.col("_sell_date") - pl.col("_buy_date"))
                .dt.total_days()
                .alias("holding_days"),
                pl.lit("closed").alias("status"),
                pl.lit(None, dtype=pl.Float64).alias("current_value"),
            ]
        )

    # --- Open lots: the unmatched tail of each buy interval.
    latest_prices = (
        _normalize_prices(prices)
        .filter(pl.col("_ref") <= current_date)
        .sort([_BT, "_mat", "_ref"])
        .group_by([_BT, "_mat"], maintain_order=True)
        .agg(pl.col("_price").last().alias("_latest_price"))
    )
    open_lots = (
        buys.join(total_sold, on=keys, how="left")
        .with_columns(pl.col("_total_s").fill_null(0.0))
        .with_columns(
            (pl.col("_b1") - pl.max_horizontal(pl.col("_b0"), pl.col("_total_s")))
            .clip(lower_bound=0.0)
            .alias("_open_qty")
        )
        .filter(pl.col("_open_qty") > 1e-9)
        .join(latest_prices, on=[_BT, "_mat"], how="left")
        .select(
            keys
            + [
                pl.col(_MAT).alias("_mat_orig"),
                pl.col("_op_date").alias("_buy_date"),
                pl.col("_open_qty").alias("_lot_qty"),
                (pl.col("_unit_buy") * pl.col("_open_qty")).alias("_lot_value"),
                pl.lit(None, dtype=pl.Date).alias("_sell_date"),
                pl.lit(0.0).alias("sell_value"),
                (pl.lit(current_date) - pl.col("_op_date"))
                .dt.total_days()
                .alias("holding_days"),
                pl.lit("open").alias("status"),
                (pl.col("_open_qty") * pl.col("_latest_price"))
                .fill_null(0.0)
                .alias("current_value"),
            ]
        )
    )

    if closed.height:
        lots = pl.concat([closed, open_lots], how="vertical")
    else:
        lots = open_lots
    if lots.height == 0:
        return pl.DataFrame()

    # --- Coupon income per lot: coupons paid between the buy date and the
    # sell date (closed) or current date (open), inclusive on both ends.
    if coupons is not None and coupons.height > 0:
        cpn_cum = (
            _normalize_coupons(coupons)
            .sort([_BT, "_mat", "_cpn_date"])
            .with_columns(
                pl.col("_cpn_unit").cum_sum().over([_BT, "_mat"]).alias("_cpn_cum")
            )
            .group_by([_BT, "_mat", "_cpn_date"], maintain_order=True)
            .agg(pl.col("_cpn_cum").last())
        )
        lots = (
            lots.with_columns(
                pl.coalesce(pl.col("_sell_date"), pl.lit(current_date)).alias(
                    "_cpn_end"
                ),
                (pl.col("_buy_date") - pl.duration(days=1)).alias("_cpn_before"),
            )
            .sort([_BT, "_mat", "_cpn_end"])
            .join_asof(
                cpn_cum.rename({"_cpn_cum": "_cpn_at_end"}),
                left_on="_cpn_end",
                right_on="_cpn_date",
                by=[_BT, "_mat"],
                strategy="backward",
                check_sortedness=False,
            )
            .sort([_BT, "_mat", "_cpn_before"])
            .join_asof(
                cpn_cum.rename({"_cpn_cum": "_cpn_at_buy"}),
                left_on="_cpn_before",
                right_on="_cpn_date",
                by=[_BT, "_mat"],
                strategy="backward",
                check_sortedness=False,
            )
            .with_columns(
                (
                    (
                        pl.col("_cpn_at_end").fill_null(0.0)
                        - pl.col("_cpn_at_buy").fill_null(0.0)
                    )
                    * pl.col("_lot_qty")
                )
                .clip(lower_bound=0.0)
                .alias("total_coupons")
            )
            .drop(["_cpn_end", "_cpn_before", "_cpn_at_end", "_cpn_at_buy"])
        )
    else:
        lots = lots.with_columns(pl.lit(0.0).alias("total_coupons"))

    # --- Per-lot return metrics (same formulas and clamps as the legacy code)
    end_value = pl.when(pl.col("status") == "closed").then(
        pl.col("sell_value")
    ).otherwise(pl.col("current_value").fill_null(0.0)) + pl.col("total_coupons")
    lots = lots.with_columns(end_value.alias("end_value"))

    valid = (pl.col("_lot_value") >= 0.01) & (pl.col("end_value") > 0)
    ratio = pl.col("end_value") / pl.col("_lot_value")
    lots = lots.with_columns(
        pl.when(valid)
        .then((ratio - 1.0) * 100.0)
        .otherwise(0.0)
        .alias("simple_return"),
        pl.when(valid & (pl.col("holding_days") >= 30))
        .then(
            ((ratio ** (365.0 / pl.col("holding_days"))) - 1.0)
            .mul(100.0)
            .clip(lower_bound=-100.0, upper_bound=1000.0)
        )
        .otherwise(0.0)
        .alias("annualized_return"),
    )

    return lots.select(
        [
            _INV,
            _BT,
            pl.col("_mat_orig").alias(_MAT),
            pl.col("_buy_date").alias(_OP_DATE),
            pl.col("_lot_qty").alias(_QTY),
            pl.col("_lot_value").alias(_OP_VALUE),
            pl.col("_sell_date").alias("sell_date"),
            "sell_value",
            "current_value",
            "holding_days",
            "status",
            "total_coupons",
            "end_value",
            "simple_return",
            "annualized_return",
        ]
    ).sort([_INV, _BT, _MAT, _OP_DATE])


def summarize_lots(
    lots: pl.DataFrame, operation_counts: pl.DataFrame | None = None
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Aggregate lot rows into per-investor and per-bond-type summaries.

    Args:
        lots: Output of :func:`calculate_lots_bulk`.
        operation_counts: Optional DataFrame with ``investor_id`` and
            ``num_operations`` columns (count of *all* operations, matching
            the legacy summary).

    Returns:
        (summary, by_bond_type) DataFrames.
    """
    if lots.height == 0:
        return pl.DataFrame(), pl.DataFrame()

    summary = (
        lots.group_by(_INV)
        .agg(
            pl.col(_OP_VALUE).sum().alias("total_invested"),
            pl.col("end_value").sum().alias("total_end_value"),
        )
        .with_columns(
            pl.when(pl.col("total_invested") > 0.0)
            .then(
                ((pl.col("total_end_value") / pl.col("total_invested")) - 1.0) * 100.0
            )
            .otherwise(0.0)
            .alias("total_return_pct"),
            (pl.col("total_end_value") - pl.col("total_invested")).alias(
                "net_position"
            ),
        )
        .sort(_INV)
    )
    if operation_counts is not None:
        summary = summary.join(operation_counts, on=_INV, how="left")

    by_bond = (
        lots.group_by([_INV, _BT])
        .agg(
            pl.col(_OP_VALUE).sum().alias("invested"),
            pl.col("end_value").sum().alias("end_value"),
        )
        .with_columns(
            ((pl.col("end_value") / pl.col("invested")) - 1.0)
            .mul(100.0)
            .fill_nan(0.0)
            .alias("return_pct"),
            (pl.col("end_value") - pl.col("invested")).alias("net_position"),
        )
        .sort([_INV, _BT])
    )
    return summary, by_bond
