import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "data" / "nifty100.db"
MARKET_CAP_PATH = BASE_DIR / "data" / "supporting" / "market_cap.xlsx"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


def load_data():
    conn = sqlite3.connect(DB_PATH)

    financial_ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    sectors = pd.read_sql(
        "SELECT * FROM sectors",
        conn
    )

    companies = pd.read_sql(
        "SELECT * FROM companies",
        conn
    )

    conn.close()
    
    market_cap = pd.read_excel(MARKET_CAP_PATH)

    return companies, sectors, financial_ratios, market_cap

def prepare_latest_data():
    companies, sectors, financial_ratios, market_cap = load_data()

    financial_ratios = (
        financial_ratios.sort_values("year")
        .groupby("company_id", as_index=False)
        .last()
    )
    
    market_cap = (
        market_cap.sort_values("year")
        .groupby("company_id", as_index=False)
        .tail(1)
    )

    valuation_df = companies.merge(
        sectors[[
            "company_id",
            "broad_sector",
            "sub_sector",
            "market_cap_category",
        ]],
        left_on="id",
        right_on="company_id",
        how="left",
    )

    valuation_df = valuation_df.merge(
        financial_ratios.drop(columns=["id"]),
        on="company_id",
        how="left",
    )

    valuation_df = valuation_df.merge(
        market_cap.drop(columns=["id", "year"]),
        on="company_id",
        how="left",
    )

    return valuation_df


def calculate_fcf_yield(df):
    df = df.copy()

    df["fcf_yield_pct"] = (
        df["free_cash_flow_cr"]
        .div(df["market_cap_crore"])
        .mul(100)
    )

    return df

def calculate_sector_pe(df):
    df = df.copy()

    sector_pe = (
        df.groupby("broad_sector")["pe_ratio"]
        .median()
        .rename("sector_median_pe")
    )

    df = df.merge(
        sector_pe,
        left_on="broad_sector",
        right_index=True,
        how="left",
    )

    return df

def assign_valuation_flags(df):
    df = df.copy()

    df["flag"] = "Fair"

    caution = df["pe_ratio"] > (df["sector_median_pe"] * 1.5)
    discount = df["pe_ratio"] < (df["sector_median_pe"] * 0.7)

    df.loc[caution, "flag"] = "Caution"
    df.loc[discount, "flag"] = "Discount"

    df["PE_vs_sector_median_pct"] = (
        (
            df["pe_ratio"] - df["sector_median_pe"]
        )
        .div(df["sector_median_pe"])
        .mul(100)
    )

    return df
def pe_trend_data():
    _, _, _, market_cap = load_data()

    pe_trend = (
        market_cap.groupby("year")["pe_ratio"]
        .median()
        .reset_index()
        .sort_values("year")
    )

    return pe_trend

def pb_vs_roe_data(df):
    return df[
        [
            "company_name",
            "pb_ratio",
            "roe_percentage",
            "broad_sector",
        ]
    ].dropna()

def ev_ebitda_comparison(df):
    return (
        df[
            [
                "company_name",
                "broad_sector",
                "ev_ebitda",
            ]
        ]
        .sort_values("ev_ebitda")
        .reset_index(drop=True)
    )

def dividend_yield_ranker(df):
    return (
        df[
            [
                "company_name",
                "broad_sector",
                "dividend_yield_pct",
            ]
        ]
        .sort_values(
            "dividend_yield_pct",
            ascending=False,
        )
        .reset_index(drop=True)
    )


def export_valuation_summary(df):
    summary = pd.DataFrame({
        "company_id": df["company_id"],
        "company_name": df["company_name"],
        "sector": df["broad_sector"],
        "P/E": df["pe_ratio"],
        "P/B": df["pb_ratio"],
        "EV/EBITDA": df["ev_ebitda"],
        "FCF_yield_pct": df["fcf_yield_pct"],
        "5yr_median_PE": df["sector_median_pe"],
        "PE_vs_sector_median_pct": df["PE_vs_sector_median_pct"],
        "flag": df["flag"],
    })

    summary.to_excel(
        OUTPUT_DIR / "valuation_summary.xlsx",
        index=False,
    )

    return summary

def export_valuation_flags(df):
    flags = df[df["flag"].isin(["Caution", "Discount"])]

    flags = pd.DataFrame({
        "company_id": flags["company_id"],
        "company_name": flags["company_name"],
        "sector": flags["broad_sector"],
        "P/E": flags["pe_ratio"],
        "5yr_median_PE": flags["sector_median_pe"],
        "PE_vs_sector_median_pct": flags["PE_vs_sector_median_pct"],
        "flag": flags["flag"],
    })

    flags.to_csv(
        OUTPUT_DIR / "valuation_flags.csv",
        index=False,
    )

    return flags

def main():
    valuation_df = prepare_latest_data()

    valuation_df = calculate_fcf_yield(valuation_df)
    valuation_df = calculate_sector_pe(valuation_df)
    valuation_df = assign_valuation_flags(valuation_df)

    export_valuation_summary(valuation_df)
    export_valuation_flags(valuation_df)
    pe_trend = pe_trend_data()
    pb_roe = pb_vs_roe_data(valuation_df)
    ev_table = ev_ebitda_comparison(valuation_df)
    dividend_rank = dividend_yield_ranker(valuation_df)

    pe_trend.to_excel(
        OUTPUT_DIR / "pe_trend.xlsx",
        index=False,
    )

    pb_roe.to_excel(
        OUTPUT_DIR / "pb_vs_roe.xlsx",
        index=False,
    )

    ev_table.to_excel(
        OUTPUT_DIR / "ev_ebitda_comparison.xlsx",
        index=False,
    )

    dividend_rank.to_excel(
        OUTPUT_DIR / "dividend_yield_ranker.xlsx",
        index=False,
    )
    print("Valuation reports generated successfully.")


if __name__ == "__main__":
    main()

