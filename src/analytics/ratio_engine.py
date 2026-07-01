import sqlite3

import pandas as pd

from src.analytics.ratios import (
    calculate_npm,
    calculate_opm,
    calculate_roe,
    calculate_roce,
    calculate_roa,
    calculate_debt_to_equity,
    calculate_interest_coverage,
    calculate_asset_turnover,
)

from src.analytics.cashflow_kpis import (
    calculate_free_cash_flow,
    calculate_capex_intensity,
    calculate_fcf_conversion,
)

from src.analytics.cagr import (
    compute_metric_cagr,
)

DB_PATH = "data/nifty100.db"

conn = sqlite3.connect(DB_PATH)

profit_loss = pd.read_sql(
    "SELECT * FROM profitandloss",
    conn,
)

balance_sheet = pd.read_sql(
    "SELECT * FROM balancesheet",
    conn,
)

cash_flow = pd.read_sql(
    "SELECT * FROM cashflow",
    conn,
)

companies = pd.read_sql(
    "SELECT * FROM companies",
    conn,
)

df = (
    profit_loss
    .merge(
        balance_sheet,
        on=["company_id", "year"],
        how="left",
    )
    .merge(
        cash_flow,
        on=["company_id", "year"],
        how="left",
    )
    .merge(
    companies[
        [
            "id",
            "book_value",
        ]
    ].rename(
        columns={
            "id": "company_id",
            "book_value": "book_value_per_share",
        }
    ),
    on="company_id",
    how="left",
    )
)

df.rename(
    columns={
        "id_x": "profit_loss_id",
        "id_y": "balance_sheet_id",
        "id": "company_master_id",
    },
    inplace=True,
)

# --------------------------
# Profitability Ratios
# --------------------------

df["net_profit_margin_pct"] = df.apply(
    lambda x: calculate_npm(
        x["net_profit"],
        x["sales"],
    ),
    axis=1,
)

df["operating_profit_margin_pct"] = df.apply(
    lambda x: calculate_opm(
        x["operating_profit"],
        x["sales"],
    ),
    axis=1,
)

df["return_on_equity_pct"] = df.apply(
    lambda x: calculate_roe(
        x["net_profit"],
        x["equity_capital"],
        x["reserves"],
    ),
    axis=1,
)

df["interest_coverage"] = df.apply(
    lambda x: calculate_interest_coverage(
        x["operating_profit"],
        x["other_income"],
        x["interest"],
    ),
    axis=1,
)

df["debt_to_equity"] = df.apply(
    lambda x: calculate_debt_to_equity(
        x["borrowings"],
        x["equity_capital"],
        x["reserves"],
    ),
    axis=1,
)

df["asset_turnover"] = df.apply(
    lambda x: calculate_asset_turnover(
        x["sales"],
        x["total_assets"],
    ),
    axis=1,
)

# --------------------------
# Cash Flow KPIs
# --------------------------

df["free_cash_flow_cr"] = df.apply(
    lambda x: calculate_free_cash_flow(
        x["operating_activity"],
        x["investing_activity"],
    ),
    axis=1,
)

df["capex_cr"] = df["investing_activity"].abs()

df["cash_from_operations_cr"] = df["operating_activity"]

# --------------------------
# CAGR Calculations
# --------------------------

df = compute_metric_cagr(
    df,
    metric="sales",
    period=5,
)

df = compute_metric_cagr(
    df,
    metric="net_profit",
    period=5,
)

df = compute_metric_cagr(
    df,
    metric="eps",
    period=5,
)
df.rename(
    columns={
        "sales_cagr_5yr": "revenue_cagr_5yr",
        "net_profit_cagr_5yr": "pat_cagr_5yr",
    },
    inplace=True,
)

# --------------------------
# Direct Mappings
# --------------------------

df["earnings_per_share"] = df["eps"]

df["dividend_payout_ratio_pct"] = df["dividend_payout"]

df["total_debt_cr"] = df["borrowings"]

ratio_df = df[
    [
        "company_id",
        "year",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "capex_cr",
        "earnings_per_share",
        "book_value_per_share",
        "dividend_payout_ratio_pct",
        "total_debt_cr",
        "cash_from_operations_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
    ]
].copy()
ratio_df["composite_quality_score"] = None


# --------------------------
# Populate financial_ratios Table
# --------------------------

try:
    # Backup existing table (only created once)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS financial_ratios_backup AS
        SELECT * FROM financial_ratios;
    """)

    # Remove existing rows
    conn.execute("DELETE FROM financial_ratios;")

    # Insert computed KPI values
    ratio_df.to_sql(
        "financial_ratios",
        conn,
        if_exists="append",
        index=False,
    )

    conn.commit()

    print("\nfinancial_ratios table populated successfully!")

except Exception as e:
    conn.rollback()
    print(f"\nError while populating financial_ratios: {e}")

finally:
    rows = pd.read_sql(
        "SELECT COUNT(*) AS total_rows FROM financial_ratios",
        conn,
    )


conn.close()