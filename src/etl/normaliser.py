import re


MONTH_MAP = {
    "jan": "01",
    "january": "01",
    "feb": "02",
    "february": "02",
    "mar": "03",
    "march": "03",
    "apr": "04",
    "april": "04",
    "may": "05",
    "jun": "06",
    "june": "06",
    "jul": "07",
    "july": "07",
    "aug": "08",
    "august": "08",
    "sep": "09",
    "september": "09",
    "oct": "10",
    "october": "10",
    "nov": "11",
    "november": "11",
    "dec": "12",
    "december": "12",
}


def normalize_year(value):

    if value is None:
        return "PARSE_ERROR"

    value = str(value).strip()

    if value == "":
        return "PARSE_ERROR"

    if value.upper() == "TTM":
        return "TTM"

    # YYYY-MM
    match = re.match(r"^(\d{4})-(\d{2})$", value)
    if match:
        return value

    # Jan-20
    match = re.match(
        r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(\d{2})$",
        value,
        re.IGNORECASE,
    )
    if match:
        month = MONTH_MAP[match.group(1).lower()]
        year = f"20{match.group(2)}"
        return f"{year}-{month}"

    # Mar 23
    match = re.match(
        r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{2})$",
        value,
        re.IGNORECASE,
    )
    if match:
        month = MONTH_MAP[match.group(1).lower()]
        year = f"20{match.group(2)}"
        return f"{year}-{month}"

    # Mar 2023
    match = re.match(
        r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})$",
        value,
        re.IGNORECASE,
    )
    if match:
        month = MONTH_MAP[match.group(1).lower()]
        year = match.group(2)
        return f"{year}-{month}"

    # March-2023
    match = re.match(
        r"^(January|February|March|April|May|June|July|August|September|October|November|December)-(\d{4})$",
        value,
        re.IGNORECASE,
    )
    if match:
        month = MONTH_MAP[match.group(1).lower()]
        year = match.group(2)
        return f"{year}-{month}"

    # Mar 2023 12m
    match = re.match(
        r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\s+\d+m?$",
        value,
        re.IGNORECASE,
    )
    if match:
        month = MONTH_MAP[match.group(1).lower()]
        year = match.group(2)
        return f"{year}-{month}"

    # FY23
    match = re.match(r"^FY\s*(\d{2})$", value, re.IGNORECASE)
    if match:
        return f"20{match.group(1)}-03"

    # FY2023
    match = re.match(r"^FY\s*(\d{4})$", value, re.IGNORECASE)
    if match:
        return f"{match.group(1)}-03"

    # 2023
    match = re.match(r"^(\d{4})$", value)
    if match:
        return f"{match.group(1)}-03"

    return "PARSE_ERROR"


def normalize_ticker(ticker):

    if ticker is None:
        return None

    ticker = str(ticker).strip().upper()

    if ticker == "":
        return ""

    return ticker