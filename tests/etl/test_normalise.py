"""Regression coverage for every supported year-normalisation form."""

import pytest

from src.etl.normaliser import normalize_year


@pytest.mark.parametrize(("raw", "expected"), [
    ("Jan-20", "2020-01"), ("dec-24", "2024-12"), ("Mar 23", "2023-03"),
    ("Sep 2022", "2022-09"), ("March-2023", "2023-03"),
    ("December-2021", "2021-12"), ("Mar 2023 12m", "2023-03"),
    ("Jan 2024 6m", "2024-01"), ("FY23", "2023-03"), ("FY 2024", "2024-03"),
    ("2023", "2023-03"), ("2024-03", "2024-03"), (" ttm ", "TTM"),
    (None, "PARSE_ERROR"), ("", "PARSE_ERROR"), ("FY", "PARSE_ERROR"),
    ("2023-13", "PARSE_ERROR"), ("2023/03", "PARSE_ERROR"), ("Mar-2", "PARSE_ERROR"),
    ("not a date", "PARSE_ERROR"),
])
def test_normalize_year_formats_and_edges(raw, expected):
    assert normalize_year(raw) == expected
