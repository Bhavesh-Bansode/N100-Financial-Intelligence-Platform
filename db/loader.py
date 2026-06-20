import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from src.etl.loader import load_excel
from src.etl.normaliser import (
    normalize_year,
    normalize_ticker
)


DB_PATH = "data/nifty100.db"
SCHEMA_PATH = "db/schema.sql"


def normalize_company_id(df):
    if "company_id" in df.columns:
        df["company_id"] = (
            df["company_id"]
            .astype(str)
            .apply(normalize_ticker)
        )
    return df


def normalize_year_column(df):
    if "year" in df.columns:
        df["year"] = (
            df["year"]
            .astype(str)
            .apply(normalize_year)
        )
    return df


def remove_duplicates(df):
    if (
        "company_id" in df.columns
        and
        "year" in df.columns
    ):
        df = df.drop_duplicates(
            subset=["company_id", "year"],
            keep="last"
        )

    return df


def remove_orphans(df, valid_ids):
    if "company_id" in df.columns:

        df = df[
            df["company_id"].isin(valid_ids)
        ]

    return df


def load_core_data():

    companies = load_excel(
        "data/raw/companies.xlsx"
    )

    profitandloss = load_excel(
        "data/raw/profitandloss.xlsx"
    )

    balancesheet = load_excel(
        "data/raw/balancesheet.xlsx"
    )

    cashflow = load_excel(
        "data/raw/cashflow.xlsx"
    )

    analysis = load_excel(
        "data/raw/analysis.xlsx"
    )

    documents = load_excel(
        "data/raw/documents.xlsx"
    )

    prosandcons = load_excel(
        "data/raw/prosandcons.xlsx"
    )

    return {
        "companies": companies,
        "profitandloss": profitandloss,
        "balancesheet": balancesheet,
        "cashflow": cashflow,
        "analysis": analysis,
        "documents": documents,
        "prosandcons": prosandcons
    }


def load_supporting_data():

    sectors = load_excel(
        "data/supporting/sectors.xlsx"
    )

    stock_prices = load_excel(
        "data/supporting/stock_prices.xlsx"
    )

    market_cap = load_excel(
        "data/supporting/market_cap.xlsx"
    )

    financial_ratios = load_excel(
        "data/supporting/financial_ratios.xlsx"
    )

    peer_groups = load_excel(
        "data/supporting/peer_groups.xlsx"
    )

    return {
        "sectors": sectors,
        "stock_prices": stock_prices,
        "market_cap": market_cap,
        "financial_ratios": financial_ratios,
        "peer_groups": peer_groups
    }

def prepare_data(core, supporting):

    audit_stats = {}

    companies = core["companies"]
    audit_stats["companies"] = {
        "rows_in": len(companies),
        "rows_out": len(companies),
        "rejected": 0
    }
    valid_ids = set(
        companies["id"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    for name in [
        "profitandloss",
        "balancesheet",
        "cashflow"
    ]:

        df = core[name]
        rows_before = len(df)
        df = normalize_company_id(df)
        df = normalize_year_column(df)

        df = df[
            df["year"] != "PARSE_ERROR"
        ]

        df = remove_duplicates(df)

        df = remove_orphans(
            df,
            valid_ids
        )
        audit_stats[name] = {
            "rows_in": rows_before,
            "rows_out": len(df),
            "rejected": rows_before - len(df)
        }
        core[name] = df

    for name in [
        "analysis",
        "documents",
        "prosandcons",
        "sectors",
        "stock_prices",
        "market_cap",
        "financial_ratios",
        "peer_groups"
    ]:

        df = (
            core.get(name)
            if name in core
            else supporting[name]
        )
        rows_before = len(df)
        df = normalize_company_id(df)

        if (
            name in ["market_cap", "financial_ratios"]
            and "year" in df.columns
        ):
            df = df.drop_duplicates(
                subset=["company_id", "year"],
                keep="last"
            )

        if (
            name == "stock_prices"
            and "date" in df.columns
        ):
            df = df.drop_duplicates(
                subset=["company_id", "date"],
                keep="last"
            )

        if (
            name == "sectors"
            and "company_id" in df.columns
        ):
            df = df.drop_duplicates(
                subset=["company_id"],
                keep="last"
            )

        df = remove_orphans(
            df,
            valid_ids
        )
        audit_stats[name] = {
            "rows_in": rows_before,
            "rows_out": len(df),
            "rejected": rows_before - len(df)
        }
        if name in supporting:
            supporting[name] = df
        else:
            core[name] = df

        df = (
            core.get(name)
            if name in core
            else supporting[name]
        )

        df = normalize_company_id(df)

        df = remove_orphans(
            df,
            valid_ids
        )

        if name in supporting:
            supporting[name] = df
        else:
            core[name] = df

    return core, supporting, audit_stats


def create_database():

    Path("data").mkdir(
        exist_ok=True
    )

    conn = sqlite3.connect(
        DB_PATH
    )

    with open(
        SCHEMA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        schema = file.read()

    conn.executescript(
        schema
    )

    conn.commit()

    return conn

def load_tables(
    conn,
    core,
    supporting,
    audit_stats
):

    audit_records = []

    for table_name, df in core.items():

        rows_in = len(df)

        start_time = datetime.now()

        df.to_sql(
            table_name,
            conn,
            if_exists="append",
            index=False
        )

        runtime = (
            datetime.now() - start_time
        ).total_seconds()

        audit_records.append({
            "table": table_name,
            "rows_in": audit_stats[table_name]["rows_in"],
            "rows_out": audit_stats[table_name]["rows_out"],
            "rejected": audit_stats[table_name]["rejected"],
            "timestamp": datetime.now(),
            "runtime_s": runtime
        })

    for table_name, df in supporting.items():

        rows_in = len(df)

        start_time = datetime.now()

        df.to_sql(
            table_name,
            conn,
            if_exists="append",
            index=False
        )

        runtime = (
            datetime.now() - start_time
        ).total_seconds()

        audit_records.append({
            "table": table_name,
            "rows_in": rows_in,
            "rows_out": rows_in,
            "rejected": 0,
            "timestamp": datetime.now(),
            "runtime_s": runtime
        })

    return pd.DataFrame(audit_records)


def print_counts(conn):

    tables = [
        "companies",
        "profitandloss",
        "balancesheet",
        "cashflow",
        "analysis",
        "documents",
        "prosandcons",
        "sectors",
        "stock_prices",
        "market_cap",
        "financial_ratios",
        "peer_groups"
    ]

    print("\nROW COUNTS\n")

    cursor = conn.cursor()

    for table in tables:

        cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        count = cursor.fetchone()[0]

        print(
            f"{table}: {count}"
        )


def main():

    core = load_core_data()

    supporting = load_supporting_data()

    core, supporting, audit_stats = prepare_data(
        core,
        supporting
    )

    conn = create_database()

    audit_df = load_tables(
        conn,
        core,
        supporting,
        audit_stats
    )

    Path("reports").mkdir(
        exist_ok=True
    )

    audit_df.to_csv(
        "reports/load_audit.csv",
        index=False
    )

    print_counts(
        conn
    )

    conn.close()

    print(
        "\nDatabase load complete."
    )


if __name__ == "__main__":
    main()