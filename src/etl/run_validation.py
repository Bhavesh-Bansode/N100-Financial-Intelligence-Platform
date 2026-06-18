import pandas as pd

from src.etl.validator import DataValidator


def main():

    failures = []

    # Load datasets

    companies = pd.read_excel(
        "data/raw/companies.xlsx",
        header=1
    )

    profit_loss = pd.read_excel(
        "data/raw/profitandloss.xlsx",
        header=1
    )

    balance_sheet = pd.read_excel(
        "data/raw/balancesheet.xlsx",
        header=1
    )

    cashflow = pd.read_excel(
        "data/raw/cashflow.xlsx",
        header=1
    )

    # --------------------
    # DQ-01
    # --------------------

    result = DataValidator.check_company_pk_uniqueness(
        companies
    )

    if not result.empty:

        result = result.copy()

        result["rule"] = "DQ-01"

        failures.append(result)

    # --------------------
    # DQ-02
    # --------------------

    for table_name, df in [
        ("profitandloss", profit_loss),
        ("balancesheet", balance_sheet),
        ("cashflow", cashflow)
    ]:

        result = DataValidator.check_annual_pk_uniqueness(
            df
        )

        if not result.empty:

            result = result.copy()

            result["rule"] = "DQ-02"

            result["table"] = table_name

            failures.append(result)

    # --------------------
    # DQ-03
    # --------------------

    for table_name, df in [
        ("profitandloss", profit_loss),
        ("balancesheet", balance_sheet),
        ("cashflow", cashflow)
    ]:

        result = DataValidator.check_fk_integrity(
            df,
            companies
        )

        if not result.empty:

            result = result.copy()

            result["rule"] = "DQ-03"

            result["table"] = table_name

            failures.append(result)

    # Save Report

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