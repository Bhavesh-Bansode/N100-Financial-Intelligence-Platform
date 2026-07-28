import pandas as pd

from dashboard.utils.db import db


class TrendAnalytics:

    @staticmethod
    def sales_trend(company_id):
        query = """
        SELECT
            year,
            sales
        FROM profitandloss
        WHERE company_id=?
        ORDER BY year
        """
        return db.fetch_dataframe(query, (company_id,))

    @staticmethod
    def net_profit_trend(company_id):
        query = """
        SELECT
            year,
            net_profit
        FROM profitandloss
        WHERE company_id=?
        ORDER BY year
        """
        return db.fetch_dataframe(query, (company_id,))

    @staticmethod
    def operating_profit_trend(company_id):
        query = """
        SELECT
            year,
            operating_profit
        FROM profitandloss
        WHERE company_id=?
        ORDER BY year
        """
        return db.fetch_dataframe(query, (company_id,))

    @staticmethod
    def eps_trend(company_id):
        query = """
        SELECT
            year,
            eps
        FROM profitandloss
        WHERE company_id=?
        ORDER BY year
        """
        return db.fetch_dataframe(query, (company_id,))

    @staticmethod
    def dividend_payout_trend(company_id):
        query = """
        SELECT
            year,
            dividend_payout
        FROM profitandloss
        WHERE company_id=?
        ORDER BY year
        """
        return db.fetch_dataframe(query, (company_id,))

    @staticmethod
    def cashflow_trend(company_id):
        query = """
        SELECT
            year,
            operating_activity,
            investing_activity,
            financing_activity,
            net_cash_flow
        FROM cashflow
        WHERE company_id=?
        ORDER BY year
        """
        return db.fetch_dataframe(query, (company_id,))

    @staticmethod
    def balance_sheet_trend(company_id):
        query = """
        SELECT
            year,
            total_assets,
            total_liabilities,
            reserves,
            borrowings
        FROM balancesheet
        WHERE company_id=?
        ORDER BY year
        """
        return db.fetch_dataframe(query, (company_id,))

    @staticmethod
    def market_cap_trend(company_id):
        query = """
        SELECT
            year,
            market_cap_crore,
            enterprise_value_crore
        FROM market_cap
        WHERE company_id=?
        ORDER BY year
        """
        return db.fetch_dataframe(query, (company_id,))

    @staticmethod
    def ratio_trend(company_id):
        query = """
        SELECT
            year,
            net_profit_margin_pct,
            operating_profit_margin_pct,
            return_on_equity_pct,
            debt_to_equity,
            interest_coverage,
            asset_turnover,
            composite_quality_score
        FROM financial_ratios
        WHERE company_id=?
        ORDER BY year
        """
        return db.fetch_dataframe(query, (company_id,))

    @staticmethod
    def stock_price_history(company_id):
        query = """
        SELECT
            date,
            open_price,
            high_price,
            low_price,
            close_price,
            adjusted_close,
            volume
        FROM stock_prices
        WHERE company_id=?
        ORDER BY date
        """
        return db.fetch_dataframe(query, (company_id,))

    @staticmethod
    def company_overview(company_id):
        query = """
        SELECT
            c.id,
            c.company_logo,
            c.company_name,
            c.chart_link,
            c.about_company,
            c.website,
            c.nse_profile,
            c.bse_profile,
            c.face_value,
            c.book_value,
            c.roce_percentage,
            c.roe_percentage,
            s.broad_sector,
            s.sub_sector,
            s.market_cap_category
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE c.id = ?
        """

        return db.fetch_dataframe(query, (company_id,))

    @staticmethod
    def yearly_summary(company_id):
        query = """
        SELECT
            p.year,
            p.sales,
            p.net_profit,
            b.total_assets,
            b.total_liabilities,
            cf.net_cash_flow
        FROM profitandloss p
        LEFT JOIN balancesheet b
            ON p.company_id=b.company_id
            AND p.year=b.year
        LEFT JOIN cashflow cf
            ON p.company_id=cf.company_id
            AND p.year=cf.year
        WHERE p.company_id=?
        ORDER BY p.year
        """
        return db.fetch_dataframe(query, (company_id,))


trend = TrendAnalytics()