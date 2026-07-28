from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from dashboard.utils.db import db
from reports.tearsheet import TearSheet

ROOT = PROJECT_ROOT

OUTPUT_DIR = ROOT / "reports" / "tearsheets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

(ROOT / "output").mkdir(parents=True, exist_ok=True)

SKIPPED = []

companies = db.fetch_dataframe("""
SELECT
    id,
    company_name
FROM companies
ORDER BY company_name
""")

tearsheet = TearSheet()

total = len(companies)

for index, (_, row) in enumerate(companies.iterrows(), start=1):

    company_id = row["id"]
    company_name = row["company_name"]

    years = db.fetch_dataframe(
        """
        SELECT COUNT(*) AS cnt
        FROM profitandloss
        WHERE company_id = ?
        """,
        (company_id,)
    ).iloc[0]["cnt"]

    if years < 3:
        SKIPPED.append(
            {
                "company_id": company_id,
                "company_name": company_name,
                "reason": "Less than 3 years of data"
            }
        )
        print(f"[{index}/{total}] Skipped: {company_name} (Insufficient data)")
        continue

    safe_name = "".join(
        c if c.isalnum() else "_" for c in company_name
    )

    filename = OUTPUT_DIR / f"{safe_name}_tearsheet.pdf"
    import traceback
    try:
        tearsheet.generate(company_id, filename)
        print(f"[{index}/{total}] Generated: {company_name}")

    except Exception:
        traceback.print_exc()

        SKIPPED.append(
            {
                "company_id": company_id,
                "company_name": company_name,
                "reason": traceback.format_exc()
            }
        )
        print(f"[{index}/{total}] Failed: {company_name}")

pd.DataFrame(SKIPPED).to_csv(
    ROOT / "output" / "skipped_tearsheets.csv",
    index=False
)

generated = total - len(SKIPPED)

print("=" * 60)
print("Batch Tearsheet Generation Completed")
print(f"Total Companies : {total}")
print(f"Generated PDFs  : {generated}")
print(f"Skipped         : {len(SKIPPED)}")
print(f"Tearsheets Path : {OUTPUT_DIR}")
print(f"Skipped Log     : {ROOT / 'output' / 'skipped_tearsheets.csv'}")
print("=" * 60)