import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../")
    )
)


from src.etl.normaliser import (
    normalize_year,
    normalize_ticker
)


def test_mar23():
    assert normalize_year("Mar-23") == "2023-03"


def test_fy24():
    assert normalize_year("FY24") == "2024-03"


def test_tcs():
    assert normalize_ticker("tcs") == "TCS"


def test_hdfc():
    assert normalize_ticker(" hdfcbank ") == "HDFCBANK"