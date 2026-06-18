import re


def normalize_year(value):
    """
    Convert various year formats into YYYY-MM.
    """

    if value is None:
        return "PARSE_ERROR"

    value = str(value).strip()

    month_map = {
        "jan": "01", "january": "01",
        "feb": "02", "february": "02",
        "mar": "03", "march": "03",
        "apr": "04", "april": "04",
        "may": "05",
        "jun": "06", "june": "06",
        "jul": "07", "july": "07",
        "aug": "08", "august": "08",
        "sep": "09", "september": "09",
        "oct": "10", "october": "10",
        "nov": "11", "november": "11",
        "dec": "12", "december": "12"
    }

    # Already normalized: 2023-03
    if re.match(r"^\d{4}-\d{2}$", value):
        return value

    # FY23
    match = re.match(r"^FY(\d{2})$", value, re.IGNORECASE)
    if match:
        return f"20{match.group(1)}-03"

    # 2023
    if re.match(r"^\d{4}$", value):
        return f"{value}-03"

    # Mar-23 or Mar 23
    match = re.match(r"^([A-Za-z]{3})[- ](\d{2})$", value)
    if match:
        month = month_map[match.group(1).lower()]
        year = f"20{match.group(2)}"
        return f"{year}-{month}"

    # March-2023
    match = re.match(r"^([A-Za-z]+)-(\d{4})$", value)
    if match:
        month_name = match.group(1).lower()

        if month_name in month_map:
            return f"{match.group(2)}-{month_map[month_name]}"

    return "PARSE_ERROR"


def normalize_ticker(ticker):
    """
    Standardize ticker symbols.
    """

    if ticker is None:
        return None

    return str(ticker).strip().upper()