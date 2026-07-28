from pathlib import Path
import sqlite3

import matplotlib

# Reports are generated in batch jobs as well as locally; no GUI backend is needed.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from src.analytics.clustering import (
    FEATURE_COLUMNS,
    generate_elbow_plot,
    impute_sector_median,
    prepare_clustering_data,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"
REPORTS_DIR = PROJECT_ROOT / "reports"

# These are the ten cross-sectional financial KPIs used in the correlation,
# outlier and distribution reports. They are all available in financial_ratios.
KPI_COLUMNS = [
    "net_profit_margin_pct", "operating_profit_margin_pct", "return_on_equity_pct",
    "debt_to_equity", "interest_coverage", "asset_turnover", "free_cash_flow_cr",
    "revenue_cagr_5yr", "pat_cagr_5yr", "eps_cagr_5yr",
]

# These labels are based on the actual constituents after fitting the
# deterministic model (random_state=42). Confirm this map with the team lead
# after any model or data change.
REVIEWED_CLUSTER_NAMES = {
    0: "Diversified Core",
    1: "High-Margin Defensives",
    2: "Emerging Growth",
    3: "Financials & Lenders",
    4: "High-Quality Compounder",
}


def load_latest_kpis(db_path: Path = DB_PATH) -> pd.DataFrame:
    """Return one latest available financial-ratio row for every company."""
    query = f"""
        SELECT fr.company_id, c.company_name, fr.year, s.broad_sector,
               {', '.join('fr.' + column for column in KPI_COLUMNS)}
        FROM financial_ratios fr
        JOIN companies c ON c.id = fr.company_id
        LEFT JOIN sectors s ON s.company_id = fr.company_id
    """
    with sqlite3.connect(db_path) as connection:
        data = pd.read_sql_query(query, connection)

    # TTM records are partial, so select the latest annual reporting period.
    # This gives one complete cross-sectional observation for all 92 companies.
    data["_year_number"] = pd.to_numeric(
        data["year"].astype(str).str.extract(r"(\d{4})")[0], errors="coerce"
    )
    data = data.dropna(subset=["_year_number"])
    data = data.sort_values(["company_id", "_year_number"])
    data = data.drop_duplicates("company_id", keep="last").drop(
        columns=["_year_number"]
    )
    data["broad_sector"] = data["broad_sector"].fillna("Unknown")
    return data.sort_values("company_id").reset_index(drop=True)


def generate_cluster_outputs(db_path: Path = DB_PATH) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Cluster companies and save labels plus mean/median feature profiles."""
    data = impute_sector_median(prepare_clustering_data(db_path)).copy()
    latest_kpis = load_latest_kpis(db_path)[["company_id", "company_name"]]
    data = data.merge(latest_kpis, on="company_id", how="left", validate="one_to_one")

    scaled = StandardScaler().fit_transform(data[FEATURE_COLUMNS])
    scaled = np.nan_to_num(scaled)
    generate_elbow_plot(scaled)
    model = KMeans(n_clusters=5, random_state=42, n_init=10)
    data["cluster_id"] = model.fit_predict(scaled)
    data["cluster_name"] = data["cluster_id"].map(REVIEWED_CLUSTER_NAMES)
    data["distance_from_centroid"] = np.linalg.norm(
        scaled - model.cluster_centers_[data["cluster_id"]], axis=1
    ).round(4)

    labels = data[[
        "company_id", "company_name", "cluster_id", "cluster_name", "distance_from_centroid"
    ]].sort_values(["cluster_id", "company_id"])

    profiles = data.groupby(["cluster_id", "cluster_name"], sort=True)[FEATURE_COLUMNS].agg(["mean", "median"])
    profiles.columns = [f"{metric}_{stat}" for metric, stat in profiles.columns]
    profiles = profiles.reset_index()
    profiles.insert(2, "company_count", data.groupby("cluster_id").size().reindex(profiles["cluster_id"]).to_numpy())

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    labels.to_csv(OUTPUT_DIR / "cluster_labels.csv", index=False)
    profiles.to_csv(OUTPUT_DIR / "cluster_profiles.csv", index=False)
    return labels, profiles


def generate_correlation_heatmap(latest_kpis: pd.DataFrame) -> pd.DataFrame:
    """Save the annotated Pearson correlation heatmap for the ten KPIs."""
    correlation = latest_kpis[KPI_COLUMNS].apply(pd.to_numeric, errors="coerce").corr(method="pearson")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(14, 11))
    sns.heatmap(correlation, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
                vmin=-1, vmax=1, square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
    plt.title("Pearson Correlation of Latest Financial KPIs (92 Companies)")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "correlation_heatmap.png", dpi=180)
    plt.close()
    return correlation


def generate_outlier_report(latest_kpis: pd.DataFrame) -> pd.DataFrame:
    """Flag companies with an absolute within-sector Z-score greater than 3."""
    records = []
    for sector, group in latest_kpis.groupby("broad_sector", dropna=False):
        for metric in KPI_COLUMNS:
            values = pd.to_numeric(group[metric], errors="coerce")
            std = values.std(ddof=0)
            if values.count() < 2 or pd.isna(std) or std == 0:
                continue
            z_scores = (values - values.mean()) / std
            for index in group.index[z_scores.abs() > 3]:
                records.append({
                    "company_id": latest_kpis.at[index, "company_id"],
                    "company_name": latest_kpis.at[index, "company_name"],
                    "broad_sector": sector, "year": latest_kpis.at[index, "year"],
                    "metric": metric, "metric_value": latest_kpis.at[index, metric],
                    "z_score": round(float(z_scores.at[index]), 4),
                    "abs_z_score": round(float(abs(z_scores.at[index])), 4),
                })
    report = pd.DataFrame(records, columns=[
        "company_id", "company_name", "broad_sector", "year", "metric",
        "metric_value", "z_score", "abs_z_score",
    ]).sort_values(["abs_z_score", "company_id"], ascending=[False, True])
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report.to_csv(OUTPUT_DIR / "outlier_report.csv", index=False)
    return report


def generate_portfolio_stats(latest_kpis: pd.DataFrame) -> pd.DataFrame:
    """Save P10 through P90, mean and standard deviation for every KPI."""
    kpis = latest_kpis[KPI_COLUMNS].apply(pd.to_numeric, errors="coerce")
    stats = pd.DataFrame({
        "P10": kpis.quantile(0.10), "P25": kpis.quantile(0.25), "P50": kpis.quantile(0.50),
        "P75": kpis.quantile(0.75), "P90": kpis.quantile(0.90), "Mean": kpis.mean(),
        "Std": kpis.std(ddof=1),
    })
    stats.index.name = "KPI"
    stats = stats.reset_index().round(4)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stats.to_csv(OUTPUT_DIR / "portfolio_stats.csv", index=False)
    return stats


def main() -> None:
    """Generate all requested cross-sectional analytics artifacts."""
    latest_kpis = load_latest_kpis()
    labels, profiles = generate_cluster_outputs()
    generate_correlation_heatmap(latest_kpis)
    outliers = generate_outlier_report(latest_kpis)
    generate_portfolio_stats(latest_kpis)
    print(f"Processed {len(latest_kpis)} companies.")
    print(f"Clustered {len(labels)} companies into {len(profiles)} profiles.")
    print(f"Flagged {len(outliers)} sector-metric outliers.")


if __name__ == "__main__":
    main()
