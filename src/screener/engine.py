import sqlite3

import pandas as pd
import yaml
DB_PATH = "data/nifty100.db"


def load_data():

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn,
    )

    market = pd.read_sql(
        "SELECT * FROM market_cap",
        conn,
    )

    profit = pd.read_sql(
        "SELECT * FROM profitandloss",
        conn,
    )

    sectors = pd.read_sql(
        "SELECT * FROM sectors",
        conn,
    )

    conn.close()

    return ratios, market, profit, sectors

def load_config():

    with open("config/screener_config.yaml", "r") as file:

        config = yaml.safe_load(file)

    return config

def prepare_data():

    ratios, market, profit, sectors = load_data()

    ratios["financial_year"] = ratios["year"].astype(str).str[:4]

    market["financial_year"] = market["year"].astype(str)

    df = pd.merge(
        ratios,
        market,
        on=["company_id", "financial_year"],
        how="left",
    )
    df.rename(
        columns={
            "year_x": "year",
            "year_y": "market_year",
        },
        inplace=True,
    )
    df = pd.merge(
        df,
        profit[["company_id", "year", "sales", "net_profit"]],
        on=["company_id", "year"],
        how="left",
    )

    df = pd.merge(
        df,
        sectors[["company_id", "broad_sector"]],
        on="company_id",
        how="left",
    )
    df.drop(
        columns=[
            "id_x",
            "id_y",
            "financial_year",
            "market_year",
        ],
        inplace=True,
    )
    return df

def get_latest_data():

    df = prepare_data()

    latest = df[df["year"] == "2024-03"].copy()

    latest = latest.reset_index(drop=True)

    return latest

def apply_filters(df, filters):

    data = df.copy()
    if filters is None:
        filters = {}
    for metric in filters:

        value = filters[metric]

        if value is None:
            continue

        if metric == "roe_min":
            data = data[data["return_on_equity_pct"] >= value]

        elif metric == "de_max":

            financial = data["broad_sector"] == "Financials"

            non_financial = data["debt_to_equity"] <= value

            data = data[financial | non_financial]

        elif metric == "fcf_min":
            data = data[data["free_cash_flow_cr"] >= value]

        elif metric == "revenue_cagr_min":
            data = data[data["revenue_cagr_5yr"] >= value]

        elif metric == "pat_cagr_min":
            data = data[data["pat_cagr_5yr"] >= value]

        elif metric == "opm_min":
            data = data[data["operating_profit_margin_pct"] >= value]

        elif metric == "pe_max":
            data = data[data["pe_ratio"] <= value]

        elif metric == "pb_max":
            data = data[data["pb_ratio"] <= value]

        elif metric == "dividend_yield_min":
            data = data[data["dividend_yield_pct"] >= value]

        elif metric == "icr_min":

            icr = data["interest_coverage"]

            data = data[
                (icr >= value)
                | (icr.astype(str).str.upper() == "DEBT FREE")
            ]

        elif metric == "market_cap_min":
            data = data[data["market_cap_crore"] >= value]

        elif metric == "net_profit_min":
            data = data[data["net_profit"] >= value]

        elif metric == "eps_cagr_min":
            data = data[data["eps_cagr_5yr"] >= value]

        elif metric == "asset_turnover_min":
            data = data[data["asset_turnover"] >= value]

        elif metric == "sales_min":
            data = data[data["sales"] >= value]

        else:
            print(f"Unknown filter : {metric}")

    return data

def calculate_score(df):

    data = df.copy()

    data["composite_quality_score"] = (
        data["return_on_equity_pct"].fillna(0)
        + data["revenue_cagr_5yr"].fillna(0)
        + data["pat_cagr_5yr"].fillna(0)
        + data["net_profit_margin_pct"].fillna(0)
    )

    data = data.sort_values(
        "composite_quality_score",
        ascending=False,
    )

    data = data.reset_index(drop=True)

    return data

if __name__ == "__main__":

    df = get_latest_data()
    presets = load_config()

    for name, filters in presets.items():

        if name == "turnaround_watch":
            print(f"{name} : Skipped")
            continue

        result = apply_filters(df, filters)
        result = calculate_score(result)

        print(f"{name} -> {len(result)} companies")

    