from typing import Optional, Tuple
import pandas as pd


def calculate_cagr(
    start_value: float,
    end_value: float,
    years: int,
) -> Tuple[Optional[float], str]:
    """
    Calculate CAGR with turnaround edge-case handling.

    Returns:
        (cagr, flag)
    """

    if years <= 0:
        return None, "INVALID_PERIOD"

    if pd.isna(start_value) or pd.isna(end_value):
        return None, "MISSING"

    if start_value == 0:
        return None, "ZERO_BASE"

    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    cagr = ((end_value / start_value) ** (1 / years) - 1) * 100

    return round(cagr, 2), "OK"


def compute_metric_cagr(
    df: pd.DataFrame,
    metric: str,
    period: int,
) -> pd.DataFrame:
    """
    Computes CAGR for one metric for every company.
    """

    df = df.sort_values(["company_id", "year"]).copy()

    results = []

    for company, grp in df.groupby("company_id"):

        grp = grp.reset_index(drop=True)

        cagr_values = []
        flags = []

        for i in range(len(grp)):

            if i < period:
                cagr_values.append(None)
                flags.append("INSUFFICIENT")
                continue

            start = grp.loc[i - period, metric]
            end = grp.loc[i, metric]

            cagr, flag = calculate_cagr(
                start,
                end,
                period,
            )

            cagr_values.append(cagr)
            flags.append(flag)

        grp[f"{metric}_cagr_{period}yr"] = cagr_values
        grp[f"{metric}_flag_{period}yr"] = flags

        results.append(grp)

    return pd.concat(results, ignore_index=True)


