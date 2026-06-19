import pandas as pd
import requests

class DataValidator:

    ### Company PK Uniqueness
    @staticmethod
    def check_company_pk_uniqueness(companies):
        return companies[
            companies.duplicated(
                subset=["id"],
                keep=False
            )
        ]
    
    ###(company_id, year) must be unique
    @staticmethod
    def check_annual_pk_uniqueness(df):
        return df[
            df.duplicated(
                subset=["company_id", "year"],
                keep=False
            )
        ]
    ### FK Integrity
    @staticmethod
    def check_fk_integrity(child_df, companies_df):
        valid_ids = set(companies_df["id"])
        return child_df[
            ~child_df["company_id"].isin(valid_ids)
        ]
    
    ###|total_assets - total_liabilities| / total_assets < 0.01
    @staticmethod
    def check_bs_balance(df):
        return df[
            (
                abs(
                    df["total_assets"]
                    - df["total_liabilities"]
                )
                / df["total_assets"]
            ) >= 0.01
        ]
    
    ### opm_percentage ≈ operating_profit / sales × 100
    ### Tolerance = 1%
    @staticmethod
    def check_opm_crosscheck(df):

        computed_opm = (
            df["operating_profit"]
            / df["sales"]
            * 100
        )

        return df[
            abs(
                df["opm_percentage"]
                - computed_opm
            ) >= 1
        ]
    
    ### sales > 0
    @staticmethod
    def check_positive_sales(df):
        return df[df["sales"] <= 0]
    
    ### YYYY-MM
    @staticmethod
    def check_year_format(df):

        return df[
            ~df["year"].astype(str).str.match(
                r"^(\d{4}-\d{2}|TTM)$"
            )
        ]
    
    ### 2 <= len(company_id) <= 12
    @staticmethod
    def check_ticker_format(df):

        return df[
            df["company_id"].notna()
            &
            (
                (df["company_id"].astype(str).str.len() < 2)
                |
                (df["company_id"].astype(str).str.len() > 12)
            )
        ]
    
    ### net_cash_flow = operating_activity + investing_activity + financing
    @staticmethod
    def check_net_cash(df):

        calculated = (
            df["operating_activity"]
            + df["investing_activity"]
            + df["financing_activity"]
        )

        return df[
            abs(
                df["net_cash_flow"]
                - calculated
            ) > 10
        ]
    
    ### fixed_assets >= 0
    @staticmethod
    def check_fixed_assets(df):

        return df[
            df["fixed_assets"] < 0
        ]
    
    ###0 <= tax_percentage <= 60
    @staticmethod
    def check_tax_range(df):

        return df[
            (df["tax_percentage"] < 0)
            |
            (df["tax_percentage"] > 60)
        ]
    
    ### dividend_payout <= 200
    @staticmethod
    def check_dividend_payout(df):

        return df[
            df["dividend_payout"] > 200
        ]
    
    ### requests.head(Annual_Report).status_code == 200
    @staticmethod
    def check_url_validity(url):

        try:
            response = requests.head(
                url,
                timeout=5
            )

            return response.status_code != 200

        except Exception:
            return True

    ### if net_profit > 0 then eps > 0
    @staticmethod
    def check_eps_consistency(df):

        return df[
            (df["net_profit"] > 0)
            &
            (df["eps"] <= 0)
        ]

    ###total_assets == total_liabilities
    @staticmethod
    def check_balance_counter(df):

        return df[
            df["total_assets"]
            !=
            df["total_liabilities"]
        ]

    ### company >= 5 years
    @staticmethod
    def check_coverage(df):

        counts = (
            df.groupby("company_id")["year"]
            .nunique()
            .reset_index(name="year_count")
        )

        return counts[
            counts["year_count"] < 5
        ]