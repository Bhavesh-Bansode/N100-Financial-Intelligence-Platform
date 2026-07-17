import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

DB_PATH = "data/nifty100.db"

def load_data():

    conn = sqlite3.connect(DB_PATH)

    peer = pd.read_sql(
        "SELECT * FROM peer_percentiles",
        conn,
    )

    conn.close()

    return peer

def get_company_data(df, company):

    data = df[
        df["company_id"] == company
    ]

    return data.iloc[0]

def get_two_companies(df, company1, company2):

    first = df[
        df["company_id"] == company1
    ].iloc[0]

    second = df[
        df["company_id"] == company2
    ].iloc[0]

    return first, second

def compare_companies(first, second):

    metrics = [
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

    labels = [
        "ROE",
        "ROCE",
        "NPM",
        "Revenue",
        "PAT",
        "EPS",
        "Asset",
        "ICR",
        "FCF",
        "D/E",
    ]

    import numpy as np
    import os

    os.makedirs(
        "output",
        exist_ok=True,
    )

    x = np.arange(len(labels))

    width = 0.35

    plt.figure(figsize=(10,5))

    plt.bar(
        x - width/2,
        first[metrics],
        width,
        label=first["company_id"],
    )

    plt.bar(
        x + width/2,
        second[metrics],
        width,
        label=second["company_id"],
    )

    plt.xticks(
        x,
        labels,
        rotation=45,
    )

    plt.ylim(0,100)

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        f"output/{first['company_id']}_vs_{second['company_id']}.png",
        dpi=300,
    )

    plt.show()

def plot_radar(company):

    metrics = [
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

    values = company[metrics].tolist()

    values.append(values[0])

    labels = [
        "ROE",
        "ROCE",
        "NPM",
        "Revenue",
        "PAT",
        "EPS",
        "Asset",
        "ICR",
        "FCF",
        "D/E",
    ]

    labels.append(labels[0])

    import numpy as np

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
    )

    fig = plt.figure(figsize=(7, 7))

    ax = plt.subplot(
        111,
        polar=True,
    )

    ax.plot(
        angles,
        values,
    )

    ax.fill(
        angles,
        values,
        alpha=0.25,
    )

    ax.set_xticks(angles[:-1])

    ax.set_xticklabels(labels[:-1])

    ax.set_ylim(0, 100)

    plt.title(company["company_id"])
    import os

    os.makedirs(
        "output",
        exist_ok=True,
    )
    plt.savefig(
        f"output/{company['company_id']}_radar_chart.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.show()

if __name__ == "__main__":

    peer = load_data()

    first, second = get_two_companies(
        peer,
        "TCS",
        "INFY",
    )

    compare_companies(
        first,
        second,
    )