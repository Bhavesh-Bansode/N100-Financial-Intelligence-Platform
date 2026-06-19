import re


def normalize_year(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    if value.upper() == "TTM":
        return "TTM"

    match = re.match(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})$", value, re.IGNORECASE)

    if match:
        month_map = {
            "jan": "01",
            "feb": "02",
            "mar": "03",
            "apr": "04",
            "may": "05",
            "jun": "06",
            "jul": "07",
            "aug": "08",
            "sep": "09",
            "oct": "10",
            "nov": "11",
            "dec": "12"
        }

        month = month_map[match.group(1).lower()]
        year = match.group(2)

        return f"{year}-{month}"

    match = re.match(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\s+\d+m?$", value, re.IGNORECASE)

    if match:
        month_map = {
            "jan": "01",
            "feb": "02",
            "mar": "03",
            "apr": "04",
            "may": "05",
            "jun": "06",
            "jul": "07",
            "aug": "08",
            "sep": "09",
            "oct": "10",
            "nov": "11",
            "dec": "12"
        }

        month = month_map[match.group(1).lower()]
        year = match.group(2)

        return f"{year}-{month}"

    match = re.match(r"^FY\s*(\d{2})$", value, re.IGNORECASE)

    if match:
        return f"20{match.group(1)}-03"

    match = re.match(r"^FY\s*(\d{4})$", value, re.IGNORECASE)

    if match:
        return f"{match.group(1)}-03"

    match = re.match(r"^(\d{4})-(\d{2})$", value)

    if match:
        return value

    return "PARSE_ERROR"


def normalize_ticker(ticker):
    if ticker is None:
        return None

    ticker = str(ticker).strip().upper()

    if ticker == "":
        return None

    return ticker