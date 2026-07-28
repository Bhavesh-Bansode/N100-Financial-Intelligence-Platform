"""Historical market-cap valuation endpoints."""

from fastapi import APIRouter, HTTPException

from src.api.main import get_db
from src.api.routers._data import rows


router = APIRouter(prefix="/market-cap", tags=["market-cap"])


@router.get("/{ticker}")
def get_market_cap_history(ticker: str):
    """Return 2019-2024 valuation multiples for a company."""
    with get_db() as connection:
        exists = connection.execute("SELECT 1 FROM companies WHERE UPPER(id) = UPPER(?)", (ticker,)).fetchone()
        if exists is None:
            raise HTTPException(status_code=404, detail=f"Company ticker '{ticker}' not found")
        history = rows(connection, """
            SELECT year, pe_ratio, pb_ratio, ev_ebitda, dividend_yield_pct
            FROM market_cap WHERE UPPER(company_id) = UPPER(?) AND year BETWEEN 2019 AND 2024
            ORDER BY year
        """, (ticker,))
    return {"ticker": ticker.upper(), "history": history}
