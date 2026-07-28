import sqlite3
from pathlib import Path

import pandas as pd

from cashflow_kpis import (
    calculate_free_cash_flow,
    calculate_cfo_quality,
    calculate_capex_intensity,
    capex_label,
    calculate_fcf_conversion,
    capital_allocation_pattern,
    distress_flag,
    cashflow_quality,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)

query = """
SELECT

    c.id AS company_id,
    c.company_name,

    cf.year,

    cf.operating_activity,
    cf.investing_activity,
    cf.financing_activity,

    pl.sales,
    pl.net_profit,
    pl.operating_profit,

    fr.debt_to_equity

FROM cashflow cf

JOIN profitandloss pl
ON cf.company_id = pl.company_id
AND cf.year = pl.year

JOIN financial_ratios fr
ON cf.company_id = fr.company_id
AND cf.year = fr.year

JOIN companies c
ON c.id = cf.company_id

ORDER BY c.id, cf.year;
"""

df = pd.read_sql(query, conn)
results = []

for _, row in df.iterrows():

    fcf = calculate_free_cash_flow(
        row["operating_activity"],
        row["investing_activity"],
    )

    cfo_quality = calculate_cfo_quality(
        row["operating_activity"],
        row["net_profit"],
    )

    capex_intensity = calculate_capex_intensity(
        row["investing_activity"],
        row["sales"],
    )

    capex_type = capex_label(capex_intensity)

    fcf_conversion = calculate_fcf_conversion(
        fcf,
        row["operating_profit"],
    )

    allocation_pattern = capital_allocation_pattern(
        row["operating_activity"],
        row["investing_activity"],
        row["financing_activity"],
        cfo_quality,
    )

    distress = distress_flag(
        cfo_quality,
        fcf,
        row["debt_to_equity"],
    )

    cf_quality = cashflow_quality(cfo_quality)

    results.append({
        "company_id": row["company_id"],
        "company_name": row["company_name"],
        "year": row["year"],

        "free_cash_flow": fcf,
        "cfo_quality": cfo_quality,
        "cashflow_quality": cf_quality,

        "capex_intensity": capex_intensity,
        "capex_label": capex_type,

        "fcf_conversion": fcf_conversion,

        "capital_allocation_pattern": allocation_pattern,

        "distress_flag": distress,
    })

result_df = pd.DataFrame(results)

# ----------------------------
# Save Outputs
# ----------------------------

cashflow_file = OUTPUT_DIR / "cashflow_intelligence.xlsx"
distress_file = OUTPUT_DIR / "distress_alerts.csv"

result_df.to_excel(cashflow_file, index=False)

result_df[result_df["distress_flag"].isin(["High", "Medium"])].to_csv(
    distress_file,
    index=False,
)

print("=" * 60)
print(f"Cashflow Intelligence : {cashflow_file}")
print(f"Distress Alerts      : {distress_file}")
print("=" * 60)

conn.close()