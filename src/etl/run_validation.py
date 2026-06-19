import pandas as pd

from src.etl.loader import load_excel
from src.etl.validator import DataValidator
from src.etl.normaliser import (
    normalize_year,
    normalize_ticker
)


def add_failure(failures, result, rule, table):

    if not result.empty:

        result = result.copy()

        result["rule"] = rule
        result["table"] = table

        failures.append(result)


def main():

    failures = []

    # ==========================
    # LOAD FILES
    # ==========================

    companies = load_excel(
        "data/raw/companies.xlsx"
    )
    companies["id"] = companies["id"].apply(
        normalize_ticker
    )
    profitandloss = load_excel(
        "data/raw/profitandloss.xlsx"
    )

    balancesheet = load_excel(
        "data/raw/balancesheet.xlsx"
    )

    cashflow = load_excel(
        "data/raw/cashflow.xlsx"
    )

    analysis = load_excel(
        "data/raw/analysis.xlsx"
    )

    documents = load_excel(
        "data/raw/documents.xlsx"
    )

    prosandcons = load_excel(
        "data/raw/prosandcons.xlsx"
    )

    for df in [
        profitandloss,
        balancesheet,
        cashflow
    ]:

        df["year"] = df["year"].apply(
            normalize_year
        )

        df["company_id"] = df["company_id"].apply(
            normalize_ticker
        )

    for df in [
        analysis,
        documents,
        prosandcons
    ]:

        df["company_id"] = df["company_id"].apply(
            normalize_ticker
        )
    # ==========================
    # DQ-01
    # ==========================

    add_failure(
        failures,
        DataValidator.check_company_pk_uniqueness(
            companies
        ),
        "DQ-01",
        "companies"
    )

    # ==========================
    # DQ-02
    # ==========================

    for table_name, df in [
        ("profitandloss", profitandloss),
        ("balancesheet", balancesheet),
        ("cashflow", cashflow)
    ]:

        add_failure(
            failures,
            DataValidator.check_annual_pk_uniqueness(df),
            "DQ-02",
            table_name
        )

    # ==========================
    # DQ-03
    # ==========================

    for table_name, df in [
        ("profitandloss", profitandloss),
        ("balancesheet", balancesheet),
        ("cashflow", cashflow),
        ("analysis", analysis),
        ("documents", documents),
        ("prosandcons", prosandcons)
    ]:

        add_failure(
            failures,
            DataValidator.check_fk_integrity(
                df,
                companies
            ),
            "DQ-03",
            table_name
        )

    # ==========================
    # DQ-04
    # ==========================

    add_failure(
        failures,
        DataValidator.check_bs_balance(
            balancesheet
        ),
        "DQ-04",
        "balancesheet"
    )

    # ==========================
    # DQ-05
    # ==========================

    add_failure(
        failures,
        DataValidator.check_opm_crosscheck(
            profitandloss
        ),
        "DQ-05",
        "profitandloss"
    )

    # ==========================
    # DQ-06
    # ==========================

    add_failure(
        failures,
        DataValidator.check_positive_sales(
            profitandloss
        ),
        "DQ-06",
        "profitandloss"
    )

    # ==========================
    # DQ-07
    # ==========================

    for table_name, df in [
        ("profitandloss", profitandloss),
        ("balancesheet", balancesheet),
        ("cashflow", cashflow)
    ]:

        add_failure(
            failures,
            DataValidator.check_year_format(df),
            "DQ-07",
            table_name
        )

    # ==========================
    # DQ-08
    # ==========================

    for table_name, df in [
        ("profitandloss", profitandloss),
        ("balancesheet", balancesheet),
        ("cashflow", cashflow),
        ("analysis", analysis),
        ("documents", documents),
        ("prosandcons", prosandcons)
    ]:

        add_failure(
            failures,
            DataValidator.check_ticker_format(df),
            "DQ-08",
            table_name
        )

    # ==========================
    # DQ-09
    # ==========================

    add_failure(
        failures,
        DataValidator.check_net_cash(
            cashflow
        ),
        "DQ-09",
        "cashflow"
    )

    # ==========================
    # DQ-10
    # ==========================

    add_failure(
        failures,
        DataValidator.check_fixed_assets(
            balancesheet
        ),
        "DQ-10",
        "balancesheet"
    )

    # ==========================
    # DQ-11
    # ==========================

    add_failure(
        failures,
        DataValidator.check_tax_range(
            profitandloss
        ),
        "DQ-11",
        "profitandloss"
    )

    # ==========================
    # DQ-12
    # ==========================

    add_failure(
        failures,
        DataValidator.check_dividend_payout(
            profitandloss
        ),
        "DQ-12",
        "profitandloss"
    )

    # ==========================
    # DQ-13
    # ==========================

   # url_failures = []

   # for _, row in documents.iterrows():

   #     url = row.get("Annual_Report")

   #     if pd.notna(url):

   #         if DataValidator.check_url_validity(url):

   #             url_failures.append(row)

   # if len(url_failures) > 0:

   #     result = pd.DataFrame(url_failures)

    #    result["rule"] = "DQ-13"
     #   result["table"] = "documents"

      #  failures.append(result)

    # ==========================
    # DQ-14
    # ==========================

    add_failure(
        failures,
        DataValidator.check_eps_consistency(
            profitandloss
        ),
        "DQ-14",
        "profitandloss"
    )

    # ==========================
    # DQ-15
    # ==========================

    add_failure(
        failures,
        DataValidator.check_balance_counter(
            balancesheet
        ),
        "DQ-15",
        "balancesheet"
    )

    # ==========================
    # DQ-16
    # ==========================

    for table_name, df in [
        ("profitandloss", profitandloss),
        ("balancesheet", balancesheet),
        ("cashflow", cashflow)
    ]:

        add_failure(
            failures,
            DataValidator.check_coverage(df),
            "DQ-16",
            table_name
        )

    # ==========================
    # SAVE REPORT
    # ==========================

    if failures:

        report = pd.concat(
            failures,
            ignore_index=True
        )

        report.to_csv(
            "reports/validation_failures.csv",
            index=False
        )

        print(
            f"{len(report)} validation issues found."
        )

    else:

        print(
            "No validation failures found."
        )


if __name__ == "__main__":
    main()