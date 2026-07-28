"""Shared SQL and serialization helpers for API route modules."""

import math
import sqlite3
from typing import Any

from fastapi import HTTPException


CORE_KPIS = [
    "net_profit_margin_pct", "operating_profit_margin_pct", "return_on_equity_pct",
    "debt_to_equity", "interest_coverage", "asset_turnover", "free_cash_flow_cr",
    "revenue_cagr_5yr", "pat_cagr_5yr", "eps_cagr_5yr",
]

LATEST_RATIOS_CTE = """
WITH latest_ratios AS (
    SELECT * FROM (
        SELECT fr.*, ROW_NUMBER() OVER (PARTITION BY company_id ORDER BY year DESC) AS row_number
        FROM financial_ratios fr
        WHERE UPPER(year) != 'TTM'
    ) WHERE row_number = 1
), latest_market_cap AS (
    SELECT * FROM (
        SELECT mc.*, ROW_NUMBER() OVER (PARTITION BY company_id ORDER BY year DESC) AS row_number
        FROM market_cap mc
    ) WHERE row_number = 1
)
"""


def rows(connection: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> list[dict]:
    return [dict(row) for row in connection.execute(query, params).fetchall()]


def parse_number(value: str | None, parameter: str) -> float | None:
    """Parse finite query parameters and return HTTP 400 on invalid values."""
    if value is None:
        return None
    try:
        parsed = float(value)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=f"{parameter} must be numeric") from error
    if not math.isfinite(parsed):
        raise HTTPException(status_code=400, detail=f"{parameter} must be finite")
    return parsed
