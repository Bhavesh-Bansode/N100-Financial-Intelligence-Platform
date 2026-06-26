def calculate_npm(net_profit, sales):
    """
    Calculate Net Profit Margin (%).
    Returns None if sales is zero.
    """

    if sales == 0:
        return None

    return (net_profit / sales) * 100


def calculate_opm(operating_profit, sales):
    """
    Calculate Operating Profit Margin (%).
    Returns None if sales is zero.
    """

    if sales == 0:
        return None

    return (operating_profit / sales) * 100


def calculate_roe(net_profit, equity_capital, reserves):
    """
    Calculate Return on Equity (%).
    Returns None if total equity is zero or negative.
    """

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return (net_profit / equity) * 100


def calculate_roce(
    operating_profit,
    depreciation,
    equity_capital,
    reserves,
    borrowings
):
    """
    Calculate Return on Capital Employed (%).

    EBIT = Operating Profit - Depreciation
    Capital Employed = Equity + Reserves + Borrowings

    Returns None if capital employed is zero or negative.
    """

    ebit = operating_profit - depreciation

    capital_employed = (
        equity_capital +
        reserves +
        borrowings
    )

    if capital_employed <= 0:
        return None

    return (ebit / capital_employed) * 100


def calculate_debt_to_equity(borrowings, equity, reserves, is_financial=False):
    """
    Calculate Debt-to-Equity ratio.
    Returns None for banks/NBFCs (carve-out).
    """

    if is_financial:
        return None

    total_equity = equity + reserves

    if total_equity <= 0:
        return None

    if borrowings == 0:
        return 0

    return (borrowings / total_equity) * 1.0

def calculate_interest_coverage(
    operating_profit,
    other_income,
    interest,
):
    """
    Calculate Interest Coverage Ratio.
    """

    if interest == 0:
        return None      # Display as "Debt Free"

    return (operating_profit + other_income) / interest

def calculate_asset_turnover(
    sales,
    total_assets,
):
    """
    Calculate Asset Turnover Ratio.
    """

    if total_assets == 0:
        return None

    return sales / total_assets


import pandas as pd

def validate_opm(
    operating_profit,
    sales,
    source_opm
):
    """
    Cross-check computed OPM against source OPM.

    Returns:
        computed_opm,
        difference,
        is_valid
    """

    computed_opm = calculate_opm(
        operating_profit,
        sales
    )

    if computed_opm is None:
        return None, None, None

    if pd.isna(source_opm):
        return computed_opm, None, None

    difference = abs(
        computed_opm - source_opm
    )

    is_valid = difference <= 1

    return (
        computed_opm,
        difference,
        is_valid
    )