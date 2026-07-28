"""Verify workbook selection and resulting schemas for representative inputs."""

from pathlib import Path

import pytest

from src.etl.loader import load_excel


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(("relative_path", "minimum_rows", "required_columns"), [
    ("data/raw/companies.xlsx", 92, {"id", "company_name"}),
    ("data/raw/profitandloss.xlsx", 1000, {"company_id", "year", "sales"}),
    ("data/raw/balancesheet.xlsx", 1000, {"company_id", "year", "total_assets"}),
    ("data/raw/cashflow.xlsx", 1000, {"company_id", "year", "net_cash_flow"}),
    ("data/raw/documents.xlsx", 1000, {"company_id", "Year", "Annual_Report"}),
    ("data/raw/prosandcons.xlsx", 10, {"company_id", "pros", "cons"}),
    ("data/supporting/sectors.xlsx", 92, {"company_id", "broad_sector", "sub_sector"}),
    ("data/supporting/market_cap.xlsx", 500, {"company_id", "year", "pe_ratio"}),
    ("data/supporting/peer_groups.xlsx", 50, {"peer_group_name", "company_id"}),
    ("data/supporting/financial_ratios.xlsx", 1000, {"company_id", "year", "return_on_equity_pct"}),
])
def test_loader_reads_expected_rows_and_columns(relative_path, minimum_rows, required_columns):
    frame = load_excel(str(ROOT / relative_path))
    assert len(frame) >= minimum_rows
    assert required_columns.issubset(frame.columns)
