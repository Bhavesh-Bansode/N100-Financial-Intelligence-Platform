from dashboard.utils.db import db


class PortfolioReport:

    @staticmethod
    def portfolio_summary(company_ids):

        placeholders = ",".join(["?"] * len(company_ids))

        query = f"""
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,
            s.market_cap_category,
            c.book_value,
            c.roe_percentage,
            c.roce_percentage
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE c.id IN ({placeholders})
        ORDER BY c.company_name
        """

        return db.fetch_dataframe(query, tuple(company_ids))

    @staticmethod
    def latest_market_cap(company_ids):

        placeholders = ",".join(["?"] * len(company_ids))

        query = f"""
        SELECT
            c.company_name,
            MAX(m.market_cap_crore) AS market_cap,
            MAX(m.enterprise_value_crore) AS enterprise_value
        FROM companies c
        JOIN market_cap m
            ON c.id = m.company_id
        WHERE c.id IN ({placeholders})
        GROUP BY c.company_name
        ORDER BY market_cap DESC
        """

        return db.fetch_dataframe(query, tuple(company_ids))

    @staticmethod
    def portfolio_quality(company_ids):

        placeholders = ",".join(["?"] * len(company_ids))

        query = f"""
        SELECT
            c.company_name,
            MAX(fr.composite_quality_score) AS quality_score,
            MAX(fr.return_on_equity_pct) AS roe,
            MAX(fr.net_profit_margin_pct) AS net_margin,
            MAX(fr.operating_profit_margin_pct) AS operating_margin
        FROM companies c
        JOIN financial_ratios fr
            ON c.id = fr.company_id
        WHERE c.id IN ({placeholders})
        GROUP BY c.company_name
        ORDER BY quality_score DESC
        """

        return db.fetch_dataframe(query, tuple(company_ids))

    @staticmethod
    def portfolio_growth(company_ids):

        placeholders = ",".join(["?"] * len(company_ids))

        query = f"""
        SELECT
            c.company_name,
            MAX(fr.revenue_cagr_5yr) AS revenue_cagr,
            MAX(fr.pat_cagr_5yr) AS pat_cagr,
            MAX(fr.eps_cagr_5yr) AS eps_cagr
        FROM companies c
        JOIN financial_ratios fr
            ON c.id = fr.company_id
        WHERE c.id IN ({placeholders})
        GROUP BY c.company_name
        ORDER BY revenue_cagr DESC
        """

        return db.fetch_dataframe(query, tuple(company_ids))

    @staticmethod
    def portfolio_leverage(company_ids):

        placeholders = ",".join(["?"] * len(company_ids))

        query = f"""
        SELECT
            c.company_name,
            MAX(fr.debt_to_equity) AS debt_to_equity,
            MAX(fr.interest_coverage) AS interest_coverage,
            MAX(fr.asset_turnover) AS asset_turnover
        FROM companies c
        JOIN financial_ratios fr
            ON c.id = fr.company_id
        WHERE c.id IN ({placeholders})
        GROUP BY c.company_name
        ORDER BY debt_to_equity
        """

        return db.fetch_dataframe(query, tuple(company_ids))

    @staticmethod
    def portfolio_cashflow(company_ids):

        placeholders = ",".join(["?"] * len(company_ids))

        query = f"""
        SELECT
            c.company_name,
            SUM(cf.operating_activity) AS operating_cashflow,
            SUM(cf.investing_activity) AS investing_cashflow,
            SUM(cf.financing_activity) AS financing_cashflow,
            SUM(cf.net_cash_flow) AS net_cashflow
        FROM companies c
        JOIN cashflow cf
            ON c.id = cf.company_id
        WHERE c.id IN ({placeholders})
        GROUP BY c.company_name
        ORDER BY operating_cashflow DESC
        """

        return db.fetch_dataframe(query, tuple(company_ids))

    @staticmethod
    def generate(company_ids):

        report = {
            "companies": PortfolioReport.portfolio_summary(company_ids),
            "market_cap": PortfolioReport.latest_market_cap(company_ids),
            "quality": PortfolioReport.portfolio_quality(company_ids),
            "growth": PortfolioReport.portfolio_growth(company_ids),
            "leverage": PortfolioReport.portfolio_leverage(company_ids),
            "cashflow": PortfolioReport.portfolio_cashflow(company_ids)
        }

        return report


portfolio_report = PortfolioReport()