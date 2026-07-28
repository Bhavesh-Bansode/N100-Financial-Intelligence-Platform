"""One exact violating row per structured DQ rule."""

import pandas as pd
import pytest

from src.etl.rules import evaluate_rule


def _result(rule_id, frame, companies=None):
    result = evaluate_rule(rule_id, frame, companies)
    assert result["rule_id"] == rule_id
    assert result["severity"] in {"critical", "error", "warning"}
    assert len(result["violations"]) >= 1


def test_dq001_company_pk(): _result("DQ001", pd.DataFrame({"id": ["A", "A"]}))
def test_dq002_annual_pk(): _result("DQ002", pd.DataFrame({"company_id": ["A", "A"], "year": ["2024-03", "2024-03"]}))
def test_dq003_fk(): _result("DQ003", pd.DataFrame({"company_id": ["BAD"]}), pd.DataFrame({"id": ["OK"]}))
def test_dq004_balance(): _result("DQ004", pd.DataFrame({"total_assets": [100], "total_liabilities": [80]}))
def test_dq005_opm(): _result("DQ005", pd.DataFrame({"operating_profit": [10], "sales": [100], "opm_percentage": [20]}))
def test_dq006_sales(): _result("DQ006", pd.DataFrame({"sales": [0]}))
def test_dq007_year(): _result("DQ007", pd.DataFrame({"year": ["2024/03"]}))
def test_dq008_ticker(): _result("DQ008", pd.DataFrame({"company_id": ["A"]}))
def test_dq009_cash(): _result("DQ009", pd.DataFrame({"operating_activity": [1], "investing_activity": [2], "financing_activity": [3], "net_cash_flow": [20]}))
def test_dq010_assets(): _result("DQ010", pd.DataFrame({"fixed_assets": [-1]}))
def test_dq011_tax(): _result("DQ011", pd.DataFrame({"tax_percentage": [61]}))
def test_dq012_dividend(): _result("DQ012", pd.DataFrame({"dividend_payout": [201]}))
def test_dq013_eps(): _result("DQ013", pd.DataFrame({"net_profit": [1], "eps": [0]}))
def test_dq014_balance_counter(): _result("DQ014", pd.DataFrame({"total_assets": [100], "total_liabilities": [99]}))
