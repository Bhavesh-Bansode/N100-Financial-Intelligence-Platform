"""Financial screener endpoint."""

from fastapi import APIRouter

from src.api.main import get_db
from src.api.routers._data import LATEST_RATIOS_CTE, parse_number, rows


router = APIRouter(prefix="/screener", tags=["screener"])


@router.get("")
def get_screener(
    min_roe: str | None = None, max_de: str | None = None, min_fcf: str | None = None,
    sector: str | None = None, min_rev_cagr_5yr: str | None = None,
    min_pat_cagr_5yr: str | None = None, max_pe: str | None = None,
):
    """Return a quality-ranked list after applying optional financial filters."""
    filters = {
        "min_roe": parse_number(min_roe, "min_roe"),
        "max_de": parse_number(max_de, "max_de"),
        "min_fcf": parse_number(min_fcf, "min_fcf"),
        "min_rev_cagr_5yr": parse_number(min_rev_cagr_5yr, "min_rev_cagr_5yr"),
        "min_pat_cagr_5yr": parse_number(min_pat_cagr_5yr, "min_pat_cagr_5yr"),
        "max_pe": parse_number(max_pe, "max_pe"),
    }
    clauses: list[str] = []
    params: list[object] = []
    fields = {
        "min_roe": ("lr.return_on_equity_pct >= ?",),
        "max_de": ("lr.debt_to_equity <= ?",),
        "min_fcf": ("lr.free_cash_flow_cr >= ?",),
        "min_rev_cagr_5yr": ("lr.revenue_cagr_5yr >= ?",),
        "min_pat_cagr_5yr": ("lr.pat_cagr_5yr >= ?",),
        "max_pe": ("lmc.pe_ratio <= ?",),
    }
    for key, value in filters.items():
        if value is not None:
            clauses.append(fields[key][0])
            params.append(value)
    if sector:
        clauses.append("LOWER(s.broad_sector) = LOWER(?)")
        params.append(sector)

    query = LATEST_RATIOS_CTE + """
        SELECT c.id AS ticker, c.company_name, s.broad_sector, s.sub_sector,
               s.market_cap_category, lr.year, lr.return_on_equity_pct, lr.debt_to_equity,
               lr.free_cash_flow_cr, lr.revenue_cagr_5yr, lr.pat_cagr_5yr,
               lr.eps_cagr_5yr, lr.net_profit_margin_pct, lr.operating_profit_margin_pct,
               lr.interest_coverage, lr.asset_turnover, lr.composite_quality_score,
               lmc.pe_ratio, lmc.pb_ratio, lmc.ev_ebitda, lmc.dividend_yield_pct
        FROM companies c
        JOIN latest_ratios lr ON lr.company_id = c.id
        LEFT JOIN sectors s ON s.company_id = c.id
        LEFT JOIN latest_market_cap lmc ON lmc.company_id = c.id
    """
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY lr.composite_quality_score DESC, c.company_name"
    with get_db() as connection:
        return rows(connection, query, tuple(params))
