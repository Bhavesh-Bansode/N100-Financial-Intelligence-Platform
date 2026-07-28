import streamlit as st
import pandas as pd

from dashboard.utils.db import db
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SETTINGS_FILE = PROJECT_ROOT / "src" / "dashboard" / "config" / "settings.json"

with open(SETTINGS_FILE, "r") as f:
    settings = json.load(f)
st.set_page_config(
    page_title="Nifty100 Financial Intelligence Platform",
    layout="wide"
)

st.title(" Nifty100 Financial Intelligence Platform")

st.markdown("---")


def get_counts():

    companies = db.fetch_one(
        "SELECT COUNT(*) AS total FROM companies"
    )

    sectors = db.fetch_one(
        "SELECT COUNT(DISTINCT broad_sector) AS total FROM sectors"
    )

    marketcap = db.fetch_one(
        """
        SELECT ROUND(SUM(market_cap_crore),2) AS total
        FROM (
            SELECT company_id,
                   MAX(market_cap_crore) market_cap_crore
            FROM market_cap
            GROUP BY company_id
        )
        """
    )

    reports = db.fetch_one(
        "SELECT COUNT(*) AS total FROM documents"
    )

    return companies, sectors, marketcap, reports


companies, sectors, marketcap, reports = get_counts()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Companies",
    companies["total"]
)

c2.metric(
    "Sectors",
    sectors["total"]
)

c3.metric(
    "Market Cap (₹ Cr)",
    f"{marketcap['total']:,.2f}"
)

c4.metric(
    "Annual Reports",
    reports["total"]
)

st.markdown("---")

st.subheader("Sector Distribution")

sector_df = db.fetch_dataframe(
    """
    SELECT
        broad_sector,
        COUNT(*) AS companies
    FROM sectors
    GROUP BY broad_sector
    ORDER BY companies DESC
    """
)

st.bar_chart(
    sector_df.set_index("broad_sector")
)

st.markdown("---")

st.subheader("Top 10 Companies by Market Capitalization")

market_df = db.fetch_dataframe(
    """
    SELECT
        c.company_name,
        MAX(m.market_cap_crore) market_cap
    FROM companies c
    JOIN market_cap m
        ON c.id=m.company_id
    GROUP BY c.company_name
    ORDER BY market_cap DESC
    LIMIT 10
    """
)

st.dataframe(
    market_df,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

st.subheader("Top 10 Quality Companies")

quality_df = db.fetch_dataframe(
    """
    SELECT
        c.company_name,
        MAX(fr.composite_quality_score) quality_score,
        MAX(fr.return_on_equity_pct) roe,
        MAX(fr.debt_to_equity) debt_to_equity
    FROM companies c
    JOIN financial_ratios fr
        ON c.id=fr.company_id
    GROUP BY c.company_name
    ORDER BY quality_score DESC
    LIMIT 10
    """
)

st.dataframe(
    quality_df,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

st.subheader("Recent Stock Prices")

price_df = db.fetch_dataframe(
    """
    SELECT
        c.company_name,
        sp.date,
        sp.close_price
    FROM stock_prices sp
    JOIN companies c
        ON sp.company_id=c.id
    ORDER BY sp.date DESC
    LIMIT 20
    """
)

st.dataframe(
    price_df,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

st.success("Dashboard Loaded Successfully")