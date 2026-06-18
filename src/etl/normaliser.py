import re


def normalize_year(value):
    """
    Convert year formats into YYYY-MM format.
    """

    if value is None:
        return None

    value = str(value).strip()

    month_map = {
        "jan": "01", "feb": "02", "mar": "03",
        "apr": "04", "may": "05", "jun": "06",
        "jul": "07", "aug": "08", "sep": "09",
        "oct": "10", "nov": "11", "dec": "12"
    }

    # Mar-23
    match = re.match(r"([A-Za-z]{3})-(\d{2})$", value)
    if match:
        month = month_map[match.group(1).lower()]
        year = f"20{match.group(2)}"
        return f"{year}-{month}"

    # FY24
    match = re.match(r"FY(\d{2})$", value, re.IGNORECASE)
    if match:
        return f"20{match.group(1)}-03"

    return value


def normalize_ticker(ticker):
    """
    Standardize ticker symbols.
    """

    if ticker is None:
        return None

    return str(ticker).strip().upper()