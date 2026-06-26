import pandas as pd

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
    ebit,
    equity_capital,
    reserves,
    borrowings,
):
    """
    Calculate Return on Capital Employed (ROCE).

    Formula:
    ROCE = EBIT / (Equity Capital + Reserves + Borrowings) × 100

    Returns None if capital employed is zero or negative.
    """

    capital_employed = (
        equity_capital
        + reserves
        + borrowings
    )

    if capital_employed <= 0:
        return None

    return round(
        (ebit / capital_employed) * 100,
        2
    )

def calculate_roa(
    net_profit,
    total_assets,
):
    """
    Return on Assets (ROA)

    Formula:
    ROA = Net Profit / Total Assets × 100
    """

    if total_assets <= 0:
        return None

    return round(
        (net_profit / total_assets) * 100,
        2
    )

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

    return round(
        borrowings / total_equity,
        2
    )

def calculate_net_debt(
    borrowings,
    investments,
):
    """
    Calculate Net Debt.

    Formula:
    Net Debt = Borrowings - Investments
    """

    return borrowings - investments

def high_leverage_flag(
    debt_to_equity,
    is_financial=False,
):
    """
    Returns True if D/E > 5
    for non-financial companies.
    """

    if is_financial:
        return False

    if debt_to_equity is None:
        return False

    return debt_to_equity > 5

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

    return round(
        (operating_profit + other_income) / interest,
        2
    )

def interest_coverage_label(
    interest_coverage,
):
    """
    Label for Interest Coverage.
    """

    if interest_coverage is None:
        return "Debt Free"

    return None

def interest_coverage_warning(
    interest_coverage,
):
    """
    Returns True if ICR < 1.5
    """

    if interest_coverage is None:
        return False

    return interest_coverage < 1.5

def calculate_asset_turnover(
    sales,
    total_assets,
):
    """
    Calculate Asset Turnover Ratio.
    """

    if total_assets == 0:
        return None

    return round(
        sales / total_assets,
        2
    )

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

