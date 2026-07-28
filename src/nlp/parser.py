import re
from pathlib import Path

import pandas as pd

# -------------------------------------------------
# Paths
# -------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "analysis.xlsx"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

PARSED_FILE = OUTPUT_DIR / "analysis_parsed.csv"
FAILURE_FILE = OUTPUT_DIR / "parse_failures.csv"

# -------------------------------------------------
# Read Excel
# -------------------------------------------------
df = pd.read_excel(INPUT_FILE, header=1)

FIELDS = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe",
]

pattern = re.compile(r"(\d+)\s*Years?:?\s*([-\d.]+)%", re.IGNORECASE)

parsed_rows = []
failed_rows = []

# -------------------------------------------------
# Parse
# -------------------------------------------------
for _, row in df.iterrows():

    company_id = row["company_id"]

    for field in FIELDS:

        value = row.get(field)

        if pd.isna(value):
            continue

        text = str(value).strip()

        match = pattern.search(text)

        if match:

            parsed_rows.append({
                "company_id": company_id,
                "metric_type": field,
                "period_years": int(match.group(1)),
                "value_pct": float(match.group(2))
            })

        else:

            failed_rows.append({
                "company_id": company_id,
                "metric_type": field,
                "raw_text": text
            })

# -------------------------------------------------
# Save Outputs
# -------------------------------------------------
parsed_df = pd.DataFrame(parsed_rows)
failed_df = pd.DataFrame(failed_rows)

parsed_df.to_csv(PARSED_FILE, index=False)
failed_df.to_csv(FAILURE_FILE, index=False)

print("=" * 50)
print(f"Parsed Records : {len(parsed_df)}")
print(f"Failed Records : {len(failed_df)}")
print(f"Saved : {PARSED_FILE}")
print(f"Saved : {FAILURE_FILE}")
print("=" * 50)