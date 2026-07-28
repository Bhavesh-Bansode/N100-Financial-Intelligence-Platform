"""KMeans clustering for NIFTY 100 companies."""

from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

np.random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"
OUTPUT_PATH = PROJECT_ROOT / "output" / "cluster_labels.csv"
ELBOW_PLOT_PATH = PROJECT_ROOT / "reports" / "elbow_plot.png"

FEATURE_COLUMNS = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


def load_latest_financial_data(db_path: Path = DB_PATH) -> pd.DataFrame:
    """Load the latest financial-ratio record and sector for each company."""
    query = """
        SELECT
            fr.company_id,
            fr.year,
            fr.return_on_equity_pct,
            fr.debt_to_equity,
            fr.revenue_cagr_5yr,
            fr.free_cash_flow_cr,
            fr.operating_profit_margin_pct,
            s.broad_sector
        FROM financial_ratios fr
        LEFT JOIN sectors s ON s.company_id = fr.company_id
    """

    with sqlite3.connect(db_path) as connection:
        data = pd.read_sql_query(query, connection)

    data["year"] = (
        data["year"]
        .astype(str)
        .str.extract(r"(\d{4})")[0]
        .astype(float)
    )
    data = data.dropna(subset=["year"]).sort_values(["company_id", "year"])
    data["year"] = data["year"].astype(int)

    return data


def calculate_fcf_cagr(financial_data: pd.DataFrame, period: int = 5) -> pd.DataFrame:
    """Calculate each company's latest available five-year FCF CAGR."""
    records = []

    for company_id, company_data in financial_data.groupby("company_id"):
        company_data = company_data.sort_values("year")
        latest = company_data.iloc[-1]
        prior = company_data[company_data["year"] == latest["year"] - period]

        fcf_cagr = np.nan
        if not prior.empty:
            old_fcf = prior.iloc[-1]["free_cash_flow_cr"]
            latest_fcf = latest["free_cash_flow_cr"]

            # CAGR is meaningful only when both cash-flow values are positive.
            if pd.notna(old_fcf) and pd.notna(latest_fcf) and old_fcf > 0 and latest_fcf > 0:
                fcf_cagr = ((latest_fcf / old_fcf) ** (1 / period) - 1) * 100

        records.append(
            {
                "company_id": company_id,
                "fcf_cagr_5yr": fcf_cagr,
            }
        )

    return pd.DataFrame(records)


def prepare_clustering_data(db_path: Path = DB_PATH) -> pd.DataFrame:
    """Build one latest-metric row per company and add FCF CAGR."""
    history = load_latest_financial_data(db_path)

    latest = (
        history.sort_values(["company_id", "year"])
        .drop_duplicates(subset="company_id", keep="last")
        .copy()
    )

    fcf_cagr = calculate_fcf_cagr(history)
    latest = latest.merge(fcf_cagr, on="company_id", how="left")

    latest["broad_sector"] = latest["broad_sector"].fillna("Unknown")
    return latest


def impute_sector_median(data: pd.DataFrame) -> pd.DataFrame:
    """Impute every feature using the median within the company's sector."""
    result = data.copy()

    for feature in FEATURE_COLUMNS:
        result[feature] = pd.to_numeric(result[feature], errors="coerce")

        sector_medians = result.groupby("broad_sector")[feature].transform("median")
        result[feature] = result[feature].fillna(sector_medians)

        # Fallback for sectors where the metric is entirely unavailable.
        result[feature] = result[feature].fillna(result[feature].median())

    missing = result[FEATURE_COLUMNS].isna().sum()

    if missing.any():
        raise ValueError("Unable to impute all clustering features.")

    return result


def cluster_name_map(cluster_centers: np.ndarray) -> dict[int, str]:
    """
    Assign readable names by overall quality/growth profile.

    The centres are in scaled feature space. Lower debt-to-equity is preferable,
    so it is subtracted from the score.
    """
    profile_score = (
        cluster_centers[:, 0]      # ROE
        - cluster_centers[:, 1]    # Debt-to-equity
        + cluster_centers[:, 2]    # Revenue CAGR
        + cluster_centers[:, 3]    # FCF CAGR
        + cluster_centers[:, 4]    # Operating profit margin
    )

    names_by_rank = [
        "Turnaround",
        "Developing",
        "Balanced",
        "Strong Performer",
        "Leader",
    ]
    ordered_cluster_ids = np.argsort(profile_score)

    return {
        int(cluster_id): names_by_rank[rank]
        for rank, cluster_id in enumerate(ordered_cluster_ids)
    }


def generate_elbow_plot(scaled_features: np.ndarray) -> None:
    """Save inertia for k=2 through k=10 to reports/elbow_plot.png."""
    if len(scaled_features) < 10:
        raise ValueError("At least 10 companies are required for the elbow plot.")

    k_values = range(2, 11)
    inertias = [
        KMeans(n_clusters=k, random_state=42, n_init=10).fit(scaled_features).inertia_
        for k in k_values
    ]

    ELBOW_PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.plot(list(k_values), inertias, marker="o")
    plt.xticks(list(k_values))
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Inertia")
    plt.title("KMeans Elbow Plot")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(ELBOW_PLOT_PATH, dpi=150)
    plt.close()


def run_kmeans(db_path: Path = DB_PATH) -> pd.DataFrame:
    """Run five-cluster KMeans and return the requested company labels."""
    data = impute_sector_median(prepare_clustering_data(db_path))
    missing_columns = [col for col in FEATURE_COLUMNS if col not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing required feature columns: {missing_columns}")
    if len(data) < 5:
        raise ValueError("At least five companies are required for KMeans clustering.")

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(data[FEATURE_COLUMNS])
    scaled_features = np.nan_to_num(scaled_features)
    generate_elbow_plot(scaled_features)

    model = KMeans(n_clusters=5, random_state=42, n_init=10)
    data["cluster_id"] = model.fit_predict(scaled_features)

    data["cluster_name"] = data["cluster_id"].map(cluster_name_map(model.cluster_centers_))
    data["distance_from_centroid"] = np.linalg.norm(
        scaled_features - model.cluster_centers_[data["cluster_id"]],
        axis=1,
    ).round(4)

    return data[
        ["company_id", "cluster_id", "cluster_name", "distance_from_centroid"]
    ].sort_values(["cluster_id", "company_id"])


def save_cluster_labels(labels: pd.DataFrame) -> Path:
    """Save clustering output to output/cluster_labels.csv."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    labels.to_csv(OUTPUT_PATH, index=False)
    return OUTPUT_PATH


def main() -> None:
    labels = run_kmeans()
    output_path = save_cluster_labels(labels)

    print(f"Cluster labels saved to: {output_path}")
    print(f"Elbow plot saved to: {ELBOW_PLOT_PATH}")
    print(f"Total companies clustered: {len(labels)}")
    print("KMeans clustering completed successfully.")


if __name__ == "__main__":
    main()