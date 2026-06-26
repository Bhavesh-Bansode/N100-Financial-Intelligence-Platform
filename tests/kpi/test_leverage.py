import pytest

from src.analytics.ratios import (
    calculate_debt_to_equity,
    calculate_net_debt,
    high_leverage_flag,
    calculate_interest_coverage,
    interest_coverage_label,
    interest_coverage_warning,
    calculate_asset_turnover,
)


def test_debt_to_equity_normal():
    assert calculate_debt_to_equity(200, 100, 300) == 0.5


def test_debt_to_equity_debt_free():
    assert calculate_debt_to_equity(0, 100, 300) == 0


def test_debt_to_equity_negative_equity():
    assert calculate_debt_to_equity(200, -100, 50) is None


def test_debt_to_equity_bank():
    assert calculate_debt_to_equity(
        5000,
        1000,
        5000,
        is_financial=True,
    ) is None


def test_interest_coverage():
    assert calculate_interest_coverage(
        1000,
        200,
        100,
    ) == 12


def test_interest_coverage_debt_free():
    assert calculate_interest_coverage(
        1000,
        200,
        0,
    ) is None


def test_asset_turnover():
    assert calculate_asset_turnover(
        1000,
        500,
    ) == 2


def test_asset_turnover_zero_assets():
    assert calculate_asset_turnover(
        1000,
        0,
    ) is None

def test_calculate_net_debt():
    assert calculate_net_debt(500, 200) == 300


def test_high_leverage_flag():
    assert high_leverage_flag(6) is True


def test_high_leverage_flag_financial():
    assert high_leverage_flag(6, is_financial=True) is False


def test_interest_coverage_label():
    assert interest_coverage_label(None) == "Debt Free"


def test_interest_coverage_warning():
    assert interest_coverage_warning(1.2) is True

