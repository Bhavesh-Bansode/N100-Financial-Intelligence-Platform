from dashboard.utils.db import db


class ScreenerReport:

    @staticmethod
    def top_quality(limit=20):

        query = """
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,
            fr.composite_quality_score,
            fr.return_on_equity_pct,
            fr.net_profit_margin_pct,
            fr.operating_profit_margin_pct,
            fr.debt_to_equity,
            fr.interest_coverage
        FROM financial_ratios fr
        JOIN companies c
            ON fr.company_id = c.id
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE fr.year = (
            SELECT MAX(year)
            FROM financial_ratios f2
            WHERE f2.company_id = fr.company_id
        )
        ORDER BY fr.composite_quality_score DESC
        LIMIT ?
        """

        return db.fetch_dataframe(query, (limit,))

    @staticmethod
    def top_revenue_growth(limit=20):

        query = """
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,
            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr,
            fr.eps_cagr_5yr
        FROM financial_ratios fr
        JOIN companies c
            ON fr.company_id = c.id
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE fr.year = (
            SELECT MAX(year)
            FROM financial_ratios f2
            WHERE f2.company_id = fr.company_id
        )
        ORDER BY fr.revenue_cagr_5yr DESC
        LIMIT ?
        """

        return db.fetch_dataframe(query, (limit,))

    @staticmethod
    def top_profitability(limit=20):

        query = """
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,
            fr.return_on_equity_pct,
            fr.net_profit_margin_pct,
            fr.operating_profit_margin_pct
        FROM financial_ratios fr
        JOIN companies c
            ON fr.company_id = c.id
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE fr.year = (
            SELECT MAX(year)
            FROM financial_ratios f2
            WHERE f2.company_id = fr.company_id
        )
        ORDER BY fr.return_on_equity_pct DESC
        LIMIT ?
        """

        return db.fetch_dataframe(query, (limit,))

    @staticmethod
    def low_debt(limit=20):

        query = """
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,
            fr.debt_to_equity,
            fr.interest_coverage
        FROM financial_ratios fr
        JOIN companies c
            ON fr.company_id = c.id
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE fr.year = (
            SELECT MAX(year)
            FROM financial_ratios f2
            WHERE f2.company_id = fr.company_id
        )
        ORDER BY fr.debt_to_equity ASC
        LIMIT ?
        """

        return db.fetch_dataframe(query, (limit,))

    @staticmethod
    def highest_market_cap(limit=20):

        query = """
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,
            m.market_cap_crore,
            m.enterprise_value_crore,
            m.pe_ratio,
            m.pb_ratio
        FROM market_cap m
        JOIN companies c
            ON m.company_id = c.id
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE m.year = (
            SELECT MAX(year)
            FROM market_cap m2
            WHERE m2.company_id = m.company_id
        )
        ORDER BY m.market_cap_crore DESC
        LIMIT ?
        """

        return db.fetch_dataframe(query, (limit,))

    @staticmethod
    def custom_screen(
        min_roe=0,
        max_debt=100,
        min_quality=0
    ):

        query = """
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,
            fr.return_on_equity_pct,
            fr.debt_to_equity,
            fr.composite_quality_score,
            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr
        FROM financial_ratios fr
        JOIN companies c
            ON fr.company_id = c.id
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE fr.year = (
            SELECT MAX(year)
            FROM financial_ratios f2
            WHERE f2.company_id = fr.company_id
        )
        AND fr.return_on_equity_pct >= ?
        AND fr.debt_to_equity <= ?
        AND fr.composite_quality_score >= ?
        ORDER BY fr.composite_quality_score DESC
        """

        return db.fetch_dataframe(
            query,
            (
                min_roe,
                max_debt,
                min_quality
            )
        )

    @staticmethod
    def generate():

        report = {
            "top_quality": ScreenerReport.top_quality(),
            "top_growth": ScreenerReport.top_revenue_growth(),
            "top_profitability": ScreenerReport.top_profitability(),
            "low_debt": ScreenerReport.low_debt(),
            "highest_market_cap": ScreenerReport.highest_market_cap()
        }

        return report


screener_report = ScreenerReport()