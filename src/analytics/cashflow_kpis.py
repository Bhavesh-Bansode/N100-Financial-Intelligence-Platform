def calculate_free_cash_flow(
    operating_activity,
    investing_activity,
):
    """
    Calculate Free Cash Flow.

    Formula:
    FCF = Operating Activity + Investing Activity
    """

    return operating_activity + investing_activity

def calculate_cfo_quality(operating_activity,net_profit):
    if net_profit is None or operating_activity is None or net_profit == 0:
        return None
    return round(operating_activity/net_profit,2)

def calculate_capex_intensity(investing_activity,sales):
    if sales is None or investing_activity is None or sales == 0:
        return None
    return round((abs(investing_activity)/ sales) * 100,2)

def capex_label(capex_intensity):
    if capex_intensity is None:
        return None
    if capex_intensity < 3:
        return "Asset Light"
    if capex_intensity <= 8:
        return "Moderate"
    return "Capital Intensive"

def calculate_fcf_conversion(
    free_cash_flow,
    operating_profit,
):

    if operating_profit is None or free_cash_flow is None or operating_profit == 0:
        return None

    return round((free_cash_flow / operating_profit) * 100,2)



def capital_allocation_pattern(
    operating_activity,
    investing_activity,
    financing_activity,
    cfo_quality,
):
    """
    Classify capital allocation pattern.
    """

    cfo = operating_activity > 0
    cfi = investing_activity > 0
    cff = financing_activity > 0

    if cfo and not cfi and not cff:
        if cfo_quality is not None and cfo_quality > 1:
            return "Shareholder Returns"
        return "Reinvestor"

    if cfo and cfi and not cff:
        return "Liquidating Assets"

    if not cfo and cfi and cff:
        return "Distress Signal"

    if not cfo and not cfi and cff:
        return "Growth Funded by Debt"

    if cfo and cfi and cff:
        return "Cash Accumulator"

    if not cfo and not cfi and not cff:
        return "Pre-Revenue"

    if cfo and not cfi and cff:
        return "Mixed"

    return "Unclassified"

def distress_flag(cfo_quality, free_cash_flow, debt_to_equity):

    if (
        cfo_quality is None
        or free_cash_flow is None
        or debt_to_equity is None
    ):
        return None

    if (
        cfo_quality < 1
        and free_cash_flow < 0
        and debt_to_equity > 1
    ):
        return "High"

    if free_cash_flow < 0 or debt_to_equity > 1:
        return "Medium"

    return "Low"

def cashflow_quality(cfo_quality):
    if cfo_quality is None:
        return None

    if cfo_quality >= 1.2:
        return "Excellent"

    if cfo_quality >= 1:
        return "Good"

    if cfo_quality >= 0.8:
        return "Average"

    return "Weak"