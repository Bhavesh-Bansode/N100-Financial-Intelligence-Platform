"""Focused unit coverage for core ratio, CAGR and cash-flow behaviours."""

import pytest

from src.analytics.cagr import calculate_cagr
from src.analytics.cashflow_kpis import calculate_cfo_quality
from src.analytics.ratios import (
    calculate_asset_turnover, calculate_debt_to_equity, calculate_interest_coverage,
    calculate_npm, calculate_opm, calculate_roe, high_leverage_flag, validate_opm,
)


def test_roe_positive_equity(): assert calculate_roe(20, 40, 60) == 20
def test_roe_negative_equity_is_none(): assert calculate_roe(20, 40, -50) is None
def test_roe_zero_equity_is_none(): assert calculate_roe(20, 0, 0) is None
def test_debt_free_is_zero(): assert calculate_debt_to_equity(0, 10, 90) == 0
def test_debt_to_equity_normal(): assert calculate_debt_to_equity(50, 10, 90) == 0.5
def test_debt_to_equity_financial_is_none(): assert calculate_debt_to_equity(50, 10, 90, True) is None
def test_interest_zero_is_none(): assert calculate_interest_coverage(20, 5, 0) is None
def test_interest_coverage_normal(): assert calculate_interest_coverage(20, 5, 5) == 5
def test_debt_over_five_is_flagged_non_financial(): assert high_leverage_flag(5.01) is True
def test_debt_over_five_is_not_flagged_financial(): assert high_leverage_flag(8, True) is False
def test_cagr_turnaround_flag(): assert calculate_cagr(-10, 20, 5) == (None, "TURNAROUND")
def test_cagr_decline_to_loss_flag(): assert calculate_cagr(10, -20, 5) == (None, "DECLINE_TO_LOSS")
def test_cagr_normal_calculation(): assert calculate_cagr(100, 200, 5) == (14.87, "OK")
def test_cagr_zero_base_flag(): assert calculate_cagr(0, 50, 5) == (None, "ZERO_BASE")
def test_opm_crosscheck_valid(): assert validate_opm(20, 100, 20.5)[2] is True
def test_opm_crosscheck_divergence_flag(): assert validate_opm(20, 100, 22)[2] is False
def test_cfo_quality_calculation(): assert calculate_cfo_quality(120, 100) == 1.2
def test_cfo_quality_zero_profit_is_none(): assert calculate_cfo_quality(120, 0) is None
def test_npm_zero_sales_is_none(): assert calculate_npm(10, 0) is None
def test_asset_turnover_zero_assets_is_none(): assert calculate_asset_turnover(100, 0) is None
