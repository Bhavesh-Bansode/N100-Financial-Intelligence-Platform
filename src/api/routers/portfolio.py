"""Portfolio-wide statistical endpoints."""

import pandas as pd
from fastapi import APIRouter

from src.api.main import get_db
from src.api.routers._data import CORE_KPIS, LATEST_RATIOS_CTE, rows


router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/stats")
def get_portfolio_stats():
    """Return P10-P90, mean and standard deviation for the ten core KPIs."""
    with get_db() as connection:
        data = rows(connection, LATEST_RATIOS_CTE + "SELECT " + ", ".join(CORE_KPIS) + " FROM latest_ratios")
    frame = pd.DataFrame(data)
    result = []
    for metric in CORE_KPIS:
        series = pd.to_numeric(frame[metric], errors="coerce")
        result.append({
            "kpi": metric, "P10": series.quantile(.10), "P25": series.quantile(.25),
            "P50": series.quantile(.50), "P75": series.quantile(.75), "P90": series.quantile(.90),
            "Mean": series.mean(), "Std": series.std(ddof=1),
        })
    return pd.DataFrame(result).round(4).where(lambda x: x.notna(), None).to_dict(orient="records")
