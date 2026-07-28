"""Ensure the Streamlit screener's underlying database view agrees with the API."""

import sqlite3
from pathlib import Path


def test_dashboard_screener_and_api_return_same_minimum_roe_tickers(client):
    """The Streamlit page selects the latest non-null ROE row; compare it to API output."""
    database = Path(__file__).resolve().parents[2] / "data" / "nifty100.db"
    with sqlite3.connect(database) as connection:
        dashboard_tickers = {
            row[0] for row in connection.execute("""
                SELECT c.id FROM companies c
                JOIN financial_ratios fr ON fr.id = (
                    SELECT id FROM financial_ratios f2
                    WHERE f2.company_id = c.id AND f2.return_on_equity_pct IS NOT NULL
                    AND UPPER(f2.year) != 'TTM'
                    ORDER BY f2.year DESC LIMIT 1
                )
                WHERE fr.return_on_equity_pct >= 15
            """)
        }
    api_tickers = {row["ticker"] for row in client.get("/api/v1/screener?min_roe=15").json()}
    assert api_tickers == dashboard_tickers
