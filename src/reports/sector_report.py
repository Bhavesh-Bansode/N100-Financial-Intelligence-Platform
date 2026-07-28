from dashboard.utils.db import db


class SectorReport:

    @staticmethod
    def get_sector_summary():

        query = """
        SELECT
            broad_sector,
            COUNT(company_id) AS total_companies
        FROM sectors
        GROUP BY broad_sector
        ORDER BY total_companies DESC
        """

        return db.fetch_dataframe(query)

    @staticmethod
    def get_sub_sector_summary():

        query = """
        SELECT
            broad_sector,
            sub_sector,
            COUNT(company_id) AS total_companies
        FROM sectors
        GROUP BY broad_sector, sub_sector
        ORDER BY broad_sector, total_companies DESC
        """

        return db.fetch_dataframe(query)

    @staticmethod
    def get_sector_companies(sector_name):

        query = """
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            s.market_cap_category,
            c.roe_percentage,
            c.roce_percentage,
            c.book_value
        FROM companies c
        JOIN sectors s
            ON c.id = s.company_id
        WHERE s.broad_sector = ?
        ORDER BY c.company_name
        """

        return db.fetch_dataframe(query, (sector_name,))

    @staticmethod
    def sector_market_cap(sector_name):

        query = """
        SELECT
            c.company_name,
            MAX(m.market_cap_crore) AS market_cap
        FROM companies c
        JOIN sectors s
            ON c.id = s.company_id
        JOIN market_cap m
            ON c.id = m.company_id
        WHERE s.broad_sector = ?
        GROUP BY c.company_name
        ORDER BY market_cap DESC
        """

        return db.fetch_dataframe(query, (sector_name,))

    @staticmethod
    def sector_quality_scores(sector_name):

        query = """
        SELECT
            c.company_name,
            MAX(fr.composite_quality_score) AS quality_score
        FROM companies c
        JOIN sectors s
            ON c.id = s.company_id
        JOIN financial_ratios fr
            ON c.id = fr.company_id
        WHERE s.broad_sector = ?
        GROUP BY c.company_name
        ORDER BY quality_score DESC
        """

        return db.fetch_dataframe(query, (sector_name,))

    @staticmethod
    def sector_profitability(sector_name):

        query = """
        SELECT
            c.company_name,
            MAX(fr.return_on_equity_pct) AS roe,
            MAX(fr.net_profit_margin_pct) AS net_margin,
            MAX(fr.operating_profit_margin_pct) AS operating_margin
        FROM companies c
        JOIN sectors s
            ON c.id = s.company_id
        JOIN financial_ratios fr
            ON c.id = fr.company_id
        WHERE s.broad_sector = ?
        GROUP BY c.company_name
        ORDER BY roe DESC
        """

        return db.fetch_dataframe(query, (sector_name,))

    @staticmethod
    def sector_leverage(sector_name):

        query = """
        SELECT
            c.company_name,
            MAX(fr.debt_to_equity) AS debt_to_equity,
            MAX(fr.interest_coverage) AS interest_coverage
        FROM companies c
        JOIN sectors s
            ON c.id = s.company_id
        JOIN financial_ratios fr
            ON c.id = fr.company_id
        WHERE s.broad_sector = ?
        GROUP BY c.company_name
        ORDER BY debt_to_equity
        """

        return db.fetch_dataframe(query, (sector_name,))

    @staticmethod
    def sector_growth(sector_name):

        query = """
        SELECT
            c.company_name,
            MAX(fr.revenue_cagr_5yr) AS revenue_cagr,
            MAX(fr.pat_cagr_5yr) AS profit_cagr,
            MAX(fr.eps_cagr_5yr) AS eps_cagr
        FROM companies c
        JOIN sectors s
            ON c.id = s.company_id
        JOIN financial_ratios fr
            ON c.id = fr.company_id
        WHERE s.broad_sector = ?
        GROUP BY c.company_name
        ORDER BY revenue_cagr DESC
        """

        return db.fetch_dataframe(query, (sector_name,))

    @staticmethod
    def generate(sector_name):

        report = {
            "sector": sector_name,
            "companies": SectorReport.get_sector_companies(sector_name),
            "market_cap": SectorReport.sector_market_cap(sector_name),
            "quality_scores": SectorReport.sector_quality_scores(sector_name),
            "profitability": SectorReport.sector_profitability(sector_name),
            "leverage": SectorReport.sector_leverage(sector_name),
            "growth": SectorReport.sector_growth(sector_name)
        }

        return report


sector_report = SectorReport()