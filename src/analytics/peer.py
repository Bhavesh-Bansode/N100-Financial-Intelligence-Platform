import sqlite3
import os
import pandas as pd
DB_PATH = "data/nifty100.db"

def load_data():

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn,
    )

    sectors = pd.read_sql(
        "SELECT * FROM sectors",
        conn,
    )

    companies = pd.read_sql(
        """
        SELECT
            id,
            company_name,
            roce_percentage,
            roe_percentage
        FROM companies
        """,
        conn,
    )

    conn.close()

    return ratios, sectors, companies

def prepare_data():

    ratios, sectors, companies = load_data()

    ratios = ratios.copy()

    ratios = ratios[
        ratios["year"] != "TTM"
    ]

    ratios["year"] = pd.to_datetime(
        ratios["year"],
        format="%Y-%m",
    )

    ratios = ratios.sort_values(
        [
            "company_id",
            "year",
        ]
    )

    latest = ratios.drop_duplicates(
        subset="company_id",
        keep="last",
    )

    data = pd.merge(
        latest,
        sectors[
            [
                "company_id",
                "broad_sector",
                "sub_sector",
            ]
        ],
        on="company_id",
        how="left",
    )

    data = pd.merge(
        data,
        companies,
        left_on="company_id",
        right_on="id",
        how="left",
    )

    data.drop(
        columns=[
            "id_x",
            "id_y",
        ],
        inplace=True,
    )

    return data

def calculate_percentile(data, column, ascending=True):

    score = data[column].rank(
        pct=True,
        ascending=ascending,
        na_option="bottom",
    )

    score = score * 100

    return score

def calculate_peer_scores(df):

    data = df.copy()

    groups = data.groupby(
        "broad_sector"
    )

    for sector, group in groups:

        index = group.index

        data.loc[index, "roe_percentile"] = calculate_percentile(
            group,
            "return_on_equity_pct",
        )

        data.loc[index, "roce_percentile"] = calculate_percentile(
            group,
            "roce_percentage",
        )

        data.loc[index, "npm_percentile"] = calculate_percentile(
            group,
            "net_profit_margin_pct",
        )

        data.loc[index, "revenue_cagr_percentile"] = calculate_percentile(
            group,
            "revenue_cagr_5yr",
        )

        data.loc[index, "pat_cagr_percentile"] = calculate_percentile(
            group,
            "pat_cagr_5yr",
        )

        data.loc[index, "eps_cagr_percentile"] = calculate_percentile(
            group,
            "eps_cagr_5yr",
        )

        data.loc[index, "asset_turnover_percentile"] = calculate_percentile(
            group,
            "asset_turnover",
        )

        data.loc[index, "interest_coverage_percentile"] = calculate_percentile(
            group,
            "interest_coverage",
        )

        data.loc[index, "fcf_percentile"] = calculate_percentile(
            group,
            "free_cash_flow_cr",
        )

        data.loc[index, "de_percentile"] = calculate_percentile(
            group,
            "debt_to_equity",
            ascending=False,
        )
    data["year"] = data["year"].dt.strftime("%Y-%m")
    return data

def save_peer_percentiles(df):

    conn = sqlite3.connect(DB_PATH)

    columns = [
        "company_id",
        "broad_sector",
        "sub_sector",
        "roe_percentile",
        "roce_percentile",
        "npm_percentile",
        "revenue_cagr_percentile",
        "pat_cagr_percentile",
        "eps_cagr_percentile",
        "asset_turnover_percentile",
        "interest_coverage_percentile",
        "fcf_percentile",
        "de_percentile",
    ]

    peer = df[columns].copy()

    peer.to_sql(
        "peer_percentiles",
        conn,
        if_exists="replace",
        index=False,
    )

    conn.close()

def get_peer_comparison(df, company):

    sector = df[
        df["company_id"] == company
    ]["broad_sector"].iloc[0]

    peer = df[
        df["broad_sector"] == sector
    ].copy()

    peer = peer.sort_values(
        "composite_quality_score",
        ascending=False,
    )

    peer = peer.reset_index(drop=True)

    return peer

def export_peer_comparison(peer, company):
    os.makedirs(
        "output",
        exist_ok=True,
    )
    peer = peer[
        [
            "company_id",
            "company_name",
            "broad_sector",
            "sub_sector",
            "roe_percentile",
            "roce_percentile",
            "npm_percentile",
            "revenue_cagr_percentile",
            "pat_cagr_percentile",
            "eps_cagr_percentile",
            "asset_turnover_percentile",
            "interest_coverage_percentile",
            "fcf_percentile",
            "de_percentile",
        ]
    ]

    peer.to_excel(
        f"output/{company}_peer_comparison.xlsx",
        index=False,
    )

    print(f"{company}_peer_comparison.xlsx created.")

if __name__ == "__main__":

    df = prepare_data()

    df = calculate_peer_scores(df)

    save_peer_percentiles(df)

    peer = get_peer_comparison(
        df,
        "TCS",
    )

    export_peer_comparison(
        peer,
        "TCS",
    )