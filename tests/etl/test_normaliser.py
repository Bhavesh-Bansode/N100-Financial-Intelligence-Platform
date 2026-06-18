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

# normalize_year() tests

def test_jan20():
    assert normalize_year("Jan-20") == "2020-01"

def test_feb21():
    assert normalize_year("Feb-21") == "2021-02"

def test_mar23():
    assert normalize_year("Mar-23") == "2023-03"

def test_apr22():
    assert normalize_year("Apr-22") == "2022-04"

def test_may24():
    assert normalize_year("May-24") == "2024-05"

def test_jun25():
    assert normalize_year("Jun-25") == "2025-06"

def test_fy24():
    assert normalize_year("FY24") == "2024-03"

def test_fy25():
    assert normalize_year("FY25") == "2025-03"

def test_fy26():
    assert normalize_year("FY26") == "2026-03"

def test_none_year():
    assert normalize_year(None) is None

def test_invalid_year():
    assert normalize_year("Invalid") == "Invalid"

def test_empty_year():
    assert normalize_year("") == ""


# normalize_ticker() tests

def test_tcs():
    assert normalize_ticker("tcs") == "TCS"

def test_hdfc():
    assert normalize_ticker(" hdfcbank ") == "HDFCBANK"
    
def test_infy():
    assert normalize_ticker("infy") == "INFY"

def test_sbin():
    assert normalize_ticker("sbin") == "SBIN"

def test_reliance():
    assert normalize_ticker("reliance") == "RELIANCE"

def test_uppercase():
    assert normalize_ticker("TCS") == "TCS"

def test_empty_ticker():
    assert normalize_ticker("") == ""

def test_none_ticker():
    assert normalize_ticker(None) is None
