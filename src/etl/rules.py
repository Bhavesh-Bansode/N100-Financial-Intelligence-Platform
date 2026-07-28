"""Structured data-quality rule runner used by validation reports and tests."""

import pandas as pd

from src.etl.validator import DataValidator


RULES = {
    "DQ001": ("critical", DataValidator.check_company_pk_uniqueness),
    "DQ002": ("critical", DataValidator.check_annual_pk_uniqueness),
    "DQ003": ("critical", DataValidator.check_fk_integrity),
    "DQ004": ("error", DataValidator.check_bs_balance),
    "DQ005": ("warning", DataValidator.check_opm_crosscheck),
    "DQ006": ("error", DataValidator.check_positive_sales),
    "DQ007": ("error", DataValidator.check_year_format),
    "DQ008": ("error", DataValidator.check_ticker_format),
    "DQ009": ("error", DataValidator.check_net_cash),
    "DQ010": ("error", DataValidator.check_fixed_assets),
    "DQ011": ("warning", DataValidator.check_tax_range),
    "DQ012": ("warning", DataValidator.check_dividend_payout),
    "DQ013": ("error", DataValidator.check_eps_consistency),
    "DQ014": ("warning", DataValidator.check_balance_counter),
}


def evaluate_rule(rule_id: str, frame: pd.DataFrame, companies: pd.DataFrame | None = None) -> dict:
    """Return violations with stable rule metadata for one deterministic DQ rule."""
    try:
        severity, check = RULES[rule_id]
    except KeyError as error:
        raise ValueError(f"Unknown DQ rule: {rule_id}") from error
    violations = check(frame, companies) if rule_id == "DQ003" else check(frame)
    return {"rule_id": rule_id, "severity": severity, "violations": violations.to_dict("records")}
