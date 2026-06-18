import pandas as pd
from src.etl.validator import DataValidator


def test_dq01_company_pk():
    df = pd.DataFrame({
        "id": ["TCS", "TCS"]
    })

    result = DataValidator.check_company_pk_uniqueness(df)

    assert len(result) == 2

def test_dq02_annual_pk():
    df = pd.DataFrame({
        "company_id": ["TCS", "TCS"],
        "year": ["2023-03", "2023-03"]
    })

    result = DataValidator.check_annual_pk_uniqueness(df)

    assert len(result) == 2

def test_dq03_fk_integrity():

    companies = pd.DataFrame({
        "id": ["TCS"]
    })

    child = pd.DataFrame({
        "company_id": ["INFY"]
    })

    result = DataValidator.check_fk_integrity(
        child,
        companies
    )

    assert len(result) == 1

def test_dq04_bs_balance():
    df=pd.DataFrame({"total_assets":[1000],
                     "total_liabilities":[950]
                     })
    
    result=DataValidator.check_bs_balance(df)
    assert len(result)==1

def test_dq05_opm_crosscheck():

    df = pd.DataFrame({
        "sales": [100],
        "operating_profit": [20],
        "opm_percentage": [30]
    })

    result = DataValidator.check_opm_crosscheck(df)

    assert len(result) == 1

def test_dq06_positive_sales():

    df = pd.DataFrame({
        "sales": [0]
    })

    result = DataValidator.check_positive_sales(df)

    assert len(result) == 1

def test_dq07_year_format():

    df = pd.DataFrame({
        "year": ["Mar-23"]
    })

    result = DataValidator.check_year_format(df)

    assert len(result) == 1

def test_dq08_ticker_format():

    df = pd.DataFrame({
        "company_id": ["A"]
    })

    result = DataValidator.check_ticker_format(df)

    assert len(result) == 1

def test_dq09_net_cash():

    df = pd.DataFrame({
        "operating_activity": [100],
        "investing_activity": [-20],
        "financing_activity": [-10],
        "net_cash_flow": [200]
    })

    result = DataValidator.check_net_cash(df)

    assert len(result) == 1

def test_dq10_fixed_assets():

    df = pd.DataFrame({
        "fixed_assets": [-10]
    })

    result = DataValidator.check_fixed_assets(df)

    assert len(result) == 1

def test_dq11_tax_range():

    df = pd.DataFrame({
        "tax_percentage": [75]
    })

    result = DataValidator.check_tax_range(df)

    assert len(result) == 1

def test_dq12_dividend_payout():

    df = pd.DataFrame({
        "dividend_payout": [250]
    })

    result = DataValidator.check_dividend_payout(df)

    assert len(result) == 1

def test_dq13_url_validity():

    assert DataValidator.check_url_validity(
        "https://invalid-url.com"
    ) is True

def test_dq14_eps_consistency():

    df = pd.DataFrame({
        "net_profit": [100],
        "eps": [0]
    })

    result = DataValidator.check_eps_consistency(df)

    assert len(result) == 1

def test_dq15_balance_counter():

    df = pd.DataFrame({
        "total_assets": [100],
        "total_liabilities": [90]
    })

    result = DataValidator.check_balance_counter(df)

    assert len(result) == 1

def test_dq16_coverage():

    df = pd.DataFrame({
        "company_id": [
            "TCS",
            "TCS",
            "TCS"
        ],
        "year": [
            "2021-03",
            "2022-03",
            "2023-03"
        ]
    })

    result = DataValidator.check_coverage(df)

    assert len(result) == 1