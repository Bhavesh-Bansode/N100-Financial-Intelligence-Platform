from src.etl.normaliser import (
    normalize_year,
    normalize_ticker
)

# ==================================================
# normalize_year() - 20 TEST CASES
# ==================================================

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

def test_jul23():
    assert normalize_year("Jul-23") == "2023-07"

def test_aug22():
    assert normalize_year("Aug-22") == "2022-08"

def test_sep21():
    assert normalize_year("Sep-21") == "2021-09"

def test_oct20():
    assert normalize_year("Oct-20") == "2020-10"

def test_fy23():
    assert normalize_year("FY23") == "2023-03"

def test_fy24():
    assert normalize_year("FY24") == "2024-03"

def test_fy25():
    assert normalize_year("FY25") == "2025-03"

def test_mar_space_23():
    assert normalize_year("Mar 23") == "2023-03"

def test_march_2023():
    assert normalize_year("March-2023") == "2023-03"

def test_year_only():
    assert normalize_year("2023") == "2023-03"

def test_already_normalized():
    assert normalize_year("2023-03") == "2023-03"

def test_none_year():
    assert normalize_year(None) == "PARSE_ERROR"

def test_invalid_year():
    assert normalize_year("Invalid") == "PARSE_ERROR"

def test_garbage():
    assert normalize_year("garbage") == "PARSE_ERROR"


# ==================================================
# normalize_ticker() - 20 TEST CASES
# ==================================================

def test_tcs():
    assert normalize_ticker("tcs") == "TCS"

def test_hdfcbank():
    assert normalize_ticker(" hdfcbank ") == "HDFCBANK"

def test_infy():
    assert normalize_ticker("infy") == "INFY"
    
def test_sbin():
    assert normalize_ticker("sbin") == "SBIN"

def test_reliance():
    assert normalize_ticker("reliance") == "RELIANCE"

def test_uppercase():
    assert normalize_ticker("TCS") == "TCS"

def test_trim_spaces():
    assert normalize_ticker("  INFY  ") == "INFY"

def test_axisbank():
    assert normalize_ticker("axisbank") == "AXISBANK"

def test_icicibank():
    assert normalize_ticker("icicibank") == "ICICIBANK"

def test_bajaj_auto():
    assert normalize_ticker("BAJAJ-AUTO") == "BAJAJ-AUTO"

def test_m_and_m():
    assert normalize_ticker("M&M") == "M&M"

def test_ltimindtree():
    assert normalize_ticker("ltimindtree") == "LTIMINDTREE"

def test_powergrid():
    assert normalize_ticker("powergrid") == "POWERGRID"

def test_ntpc():
    assert normalize_ticker("ntpc") == "NTPC"

def test_titan():
    assert normalize_ticker("titan") == "TITAN"

def test_sunpharma():
    assert normalize_ticker("sunpharma") == "SUNPHARMA"

def test_nested_spaces():
    assert normalize_ticker("   TCS   ") == "TCS"

def test_empty_ticker():
    assert normalize_ticker("") == ""

def test_none_ticker():
    assert normalize_ticker(None) is None

def test_already_clean():
    assert normalize_ticker("HDFCBANK") == "HDFCBANK"