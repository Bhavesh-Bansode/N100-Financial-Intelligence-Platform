"""Sector summary and constituent endpoints."""

from statistics import median

from fastapi import APIRouter, HTTPException

from src.api.main import get_db
from src.api.routers._data import LATEST_RATIOS_CTE, rows


router = APIRouter(prefix="/sectors", tags=["sectors"])


@router.get("")
def get_sectors():
    """Return counts and median ROE, P/E and D/E for each available sector."""
    query = LATEST_RATIOS_CTE + """
        SELECT s.broad_sector, lr.return_on_equity_pct, lr.debt_to_equity, lmc.pe_ratio
        FROM sectors s
        JOIN latest_ratios lr ON lr.company_id = s.company_id
        LEFT JOIN latest_market_cap lmc ON lmc.company_id = s.company_id
        WHERE s.broad_sector IS NOT NULL
        ORDER BY s.broad_sector
    """
    with get_db() as connection:
        data = rows(connection, query)
    summaries = []
    for sector in sorted({record["broad_sector"] for record in data}):
        group = [record for record in data if record["broad_sector"] == sector]
        def med(field: str):
            values = [record[field] for record in group if record[field] is not None]
            return median(values) if values else None
        summaries.append({
            "broad_sector": sector, "company_count": len(group), "median_roe": med("return_on_equity_pct"),
            "median_pe": med("pe_ratio"), "median_de": med("debt_to_equity"),
        })
    return summaries


@router.get("/{sector}/companies")
def get_sector_companies(sector: str):
    """Return all companies and latest annual KPIs for a sector."""
    query = LATEST_RATIOS_CTE + """
        SELECT c.id AS ticker, c.company_name, s.broad_sector, s.sub_sector,
               lr.year, lr.net_profit_margin_pct, lr.operating_profit_margin_pct,
               lr.return_on_equity_pct, lr.debt_to_equity, lr.interest_coverage,
               lr.asset_turnover, lr.free_cash_flow_cr, lr.revenue_cagr_5yr,
               lr.pat_cagr_5yr, lr.eps_cagr_5yr, lr.composite_quality_score
        FROM sectors s
        JOIN companies c ON c.id = s.company_id
        JOIN latest_ratios lr ON lr.company_id = c.id
        WHERE LOWER(s.broad_sector) = LOWER(?)
        ORDER BY c.company_name
    """
    with get_db() as connection:
        companies = rows(connection, query, (sector,))
    if not companies:
        raise HTTPException(status_code=404, detail=f"Sector '{sector}' not found")
    return companies
