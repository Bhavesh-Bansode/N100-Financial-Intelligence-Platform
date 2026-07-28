import sqlite3
from pathlib import Path
import pandas as pd

# ----------------------------
# Paths
# ----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "pros_cons_generated.csv"

# ----------------------------
# Connect
# ----------------------------
conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    c.id AS company_id,
    c.company_name,
    c.roce_percentage,
    c.roe_percentage,

    fr.operating_profit_margin_pct,
    fr.debt_to_equity,
    fr.interest_coverage,
    fr.free_cash_flow_cr,
    fr.revenue_cagr_5yr,
    fr.pat_cagr_5yr,
    fr.eps_cagr_5yr,
    fr.dividend_payout_ratio_pct,

    mc.pe_ratio,
    mc.pb_ratio,
    mc.dividend_yield_pct

FROM companies c

LEFT JOIN financial_ratios fr
ON fr.company_id = c.id
AND fr.year = (
    SELECT MAX(year)
    FROM financial_ratios f2
    WHERE f2.company_id = c.id
)

LEFT JOIN market_cap mc
ON mc.company_id = c.id
AND mc.year = (
    SELECT MAX(year)
    FROM market_cap m2
    WHERE m2.company_id = c.id
) """

df = pd.read_sql(query, conn)

results = []

for _, row in df.iterrows():

    pros = []
    cons = []

    # ---------------- PROS ----------------

    if pd.notna(row["roce_percentage"]) and row["roce_percentage"] >= 20:
        pros.append("High ROCE (>20%)")

    if pd.notna(row["roe_percentage"]) and row["roe_percentage"] >= 15:
        pros.append("Strong ROE")

    if pd.notna(row["operating_profit_margin_pct"]) and row["operating_profit_margin_pct"] >= 20:
        pros.append("Healthy operating margin")

    if pd.notna(row["debt_to_equity"]) and row["debt_to_equity"] <= 0.5:
        pros.append("Low debt")

    if pd.notna(row["interest_coverage"]) and row["interest_coverage"] >= 5:
        pros.append("Comfortable interest coverage")

    if pd.notna(row["free_cash_flow_cr"]) and row["free_cash_flow_cr"] > 0:
        pros.append("Positive free cash flow")

    if pd.notna(row["revenue_cagr_5yr"]) and row["revenue_cagr_5yr"] >= 10:
        pros.append("Healthy revenue growth")

    if pd.notna(row["pat_cagr_5yr"]) and row["pat_cagr_5yr"] >= 10:
        pros.append("Healthy profit growth")

    if pd.notna(row["eps_cagr_5yr"]) and row["eps_cagr_5yr"] >= 10:
        pros.append("EPS growing consistently")

    if pd.notna(row["dividend_yield_pct"]) and row["dividend_yield_pct"] >= 2:
        pros.append("Good dividend yield")

    # ---------------- CONS ----------------

    if pd.notna(row["roce_percentage"]) and row["roce_percentage"] < 10:
        cons.append("Low ROCE")

    if pd.notna(row["roe_percentage"]) and row["roe_percentage"] < 10:
        cons.append("Weak ROE")

    if pd.notna(row["debt_to_equity"]) and row["debt_to_equity"] > 1:
        cons.append("High debt")

    if pd.notna(row["interest_coverage"]) and row["interest_coverage"] < 2:
        cons.append("Weak interest coverage")

    if pd.notna(row["free_cash_flow_cr"]) and row["free_cash_flow_cr"] < 0:
        cons.append("Negative free cash flow")

    if pd.notna(row["revenue_cagr_5yr"]) and row["revenue_cagr_5yr"] < 5:
        cons.append("Slow revenue growth")

    if pd.notna(row["pat_cagr_5yr"]) and row["pat_cagr_5yr"] < 5:
        cons.append("Slow profit growth")

    if pd.notna(row["eps_cagr_5yr"]) and row["eps_cagr_5yr"] < 5:
        cons.append("Weak EPS growth")

    if pd.notna(row["pe_ratio"]) and row["pe_ratio"] > 40:
        cons.append("Expensive valuation")

    if pd.notna(row["operating_profit_margin_pct"]) and row["operating_profit_margin_pct"] < 10:
        cons.append("Low operating margin")

    results.append({
        "company_id": row["company_id"],
        "company_name": row["company_name"],
        "pros": "; ".join(pros) if pros else "None",
        "cons": "; ".join(cons) if cons else "None",
        "confidence_score": round((len(pros) + len(cons)) / 20, 2)
    })

result_df = pd.DataFrame(results)

result_df.to_csv(OUTPUT_FILE, index=False)

print("=" * 50)
print(f"Companies processed : {len(result_df)}")
print(f"Output saved to : {OUTPUT_FILE}")
print("=" * 50)

conn.close()