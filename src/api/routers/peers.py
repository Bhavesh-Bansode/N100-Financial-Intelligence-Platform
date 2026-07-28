"""Peer-group analytics endpoints."""

from fastapi import APIRouter, HTTPException
import pandas as pd

from src.api.main import get_db
from src.api.routers._data import CORE_KPIS, LATEST_RATIOS_CTE, rows


router = APIRouter(prefix="/peers", tags=["peers"])


@router.get("/{group_name}")
def get_peer_group(group_name: str):
    """Return group members and within-group percentile ranks for ten KPIs."""
    query = LATEST_RATIOS_CTE + """
        SELECT pg.peer_group_name, pg.is_benchmark, c.id AS ticker, c.company_name,
               s.broad_sector, lr.net_profit_margin_pct, lr.operating_profit_margin_pct,
               lr.return_on_equity_pct, lr.debt_to_equity, lr.interest_coverage,
               lr.asset_turnover, lr.free_cash_flow_cr, lr.revenue_cagr_5yr,
               lr.pat_cagr_5yr, lr.eps_cagr_5yr
        FROM peer_groups pg
        JOIN companies c ON c.id = pg.company_id
        JOIN latest_ratios lr ON lr.company_id = c.id
        LEFT JOIN sectors s ON s.company_id = c.id
        WHERE LOWER(pg.peer_group_name) = LOWER(?)
        ORDER BY c.company_name
    """
    with get_db() as connection:
        members = rows(connection, query, (group_name,))
    if not members:
        raise HTTPException(status_code=404, detail=f"Peer group '{group_name}' not found")
    frame = pd.DataFrame(members)
    for metric in CORE_KPIS:
        ascending = metric == "debt_to_equity"
        frame[f"{metric}_percentile"] = frame[metric].rank(
            pct=True, ascending=ascending, na_option="bottom"
        ).mul(100).round(2)
    return frame.where(frame.notna(), None).to_dict(orient="records")
