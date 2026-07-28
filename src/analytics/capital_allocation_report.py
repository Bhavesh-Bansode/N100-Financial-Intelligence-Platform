from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "output"

INPUT_FILE = OUTPUT_DIR / "cashflow_intelligence.xlsx"

df = pd.read_excel(INPUT_FILE)

# ---------------------------------------
# Capital Allocation Pattern Summary
# ---------------------------------------

pattern_summary = (
    df.groupby("capital_allocation_pattern")
      .size()
      .reset_index(name="company_count")
      .sort_values("company_count", ascending=False)
)


# ---------------------------------------
# Save Report
# ---------------------------------------

REPORT_FILE = OUTPUT_DIR / "pattern_changes.csv"

pattern_summary.to_csv(REPORT_FILE, index=False)

print("=" * 60)
print(f"Pattern report saved to : {REPORT_FILE}")
print("=" * 60)