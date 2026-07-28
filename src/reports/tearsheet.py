import matplotlib.pyplot as plt
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)
from pathlib import Path
import tempfile
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analytics.trends import trend


OUTPUT_DIR = PROJECT_ROOT / "output"

PROS_FILE = OUTPUT_DIR / "pros_cons_generated.csv"
CAPITAL_FILE = OUTPUT_DIR / "cashflow_intelligence.xlsx"


styles = getSampleStyleSheet()

TITLE = styles["Heading1"]
TITLE.alignment = TA_CENTER

NORMAL = styles["BodyText"]
NORMAL.wordWrap = "CJK"


NAVY = colors.HexColor("#0B1F4D")
GREEN = colors.HexColor("#0A8A2A")
RED = colors.HexColor("#C62828")
ORANGE = colors.HexColor("#F39C12")


class TearSheet:

    def __init__(self):

        self.trend = trend

        if PROS_FILE.exists():
            self.pros_df = pd.read_csv(PROS_FILE)
        else:
            self.pros_df = pd.DataFrame()

        if CAPITAL_FILE.exists():
            self.capital_df = pd.read_excel(CAPITAL_FILE)
        else:
            self.capital_df = pd.DataFrame()

    def save_plot(self, fig):

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")

        fig.savefig(
            tmp.name,
            dpi=180,
            bbox_inches="tight"
        )

        plt.close(fig)

        return tmp.name

    def sales_chart(self, df):

        fig, ax = plt.subplots(figsize=(5, 3))

        ax.bar(df["year"], df["sales"])

        ax.set_title("Revenue Trend")

        ax.tick_params(axis="x", rotation=45)

        return self.save_plot(fig)

    def profit_chart(self, df):

        fig, ax = plt.subplots(figsize=(5, 3))

        ax.bar(df["year"], df["net_profit"])

        ax.set_title("Net Profit Trend")

        ax.tick_params(axis="x", rotation=45)

        return self.save_plot(fig)

    def roe_chart(self, df):

        fig, ax = plt.subplots(figsize=(6, 3))

        ax.plot(
            df["year"],
            df["return_on_equity_pct"],
            marker="o",
            label="ROE"
        )

        ax.legend()

        ax.tick_params(axis="x", rotation=45)

        return self.save_plot(fig)

    def balance_chart(self, df):

        fig, ax = plt.subplots(figsize=(6, 3))

        equity = (
            df["total_assets"] -
            df["total_liabilities"]
        )

        ax.bar(
            df["year"],
            equity,
            label="Equity"
        )

        ax.bar(
            df["year"],
            df["borrowings"],
            bottom=equity,
            label="Borrowings"
        )

        ax.legend()

        ax.tick_params(axis="x", rotation=45)

        return self.save_plot(fig)

    def cashflow_chart(self, latest):

        labels = [
            "Operating",
            "Investing",
            "Financing",
            "Net"
        ]

        values = [

            latest["operating_activity"],

            latest["investing_activity"],

            latest["financing_activity"],

            latest["net_cash_flow"]
        ]

        fig, ax = plt.subplots(figsize=(6, 3))

        ax.bar(labels, values)

        ax.set_title("Cash Flow")

        return self.save_plot(fig)

    def get_pros(self, company_id):

        if self.pros_df.empty:
            return []

        df = self.pros_df[
            self.pros_df["company_id"] == company_id
        ]

        if df.empty:
            return []

        text = df.iloc[-1]["pros"]

        if pd.isna(text) or str(text).strip() == "":
            return []

        return [item.strip() for item in str(text).split(";") if item.strip()]
    
    def get_cons(self, company_id):

        if self.pros_df.empty:
            return []

        df = self.pros_df[
            self.pros_df["company_id"] == company_id
        ]

        if df.empty:
            return []

        text = df.iloc[-1]["cons"]

        if pd.isna(text) or str(text).strip() == "":
            return []

        return [item.strip() for item in str(text).split(";") if item.strip()]
    
    def capital_label(self, company_id):

        if self.capital_df.empty:
            return "Not Available"

        df = self.capital_df[
            self.capital_df["company_id"] == company_id
        ]

        if df.empty:
            return "Not Available"

        return df.iloc[-1]["capital_allocation_pattern"]

    
    def fmt(self, value, suffix=""):
        if value is None or pd.isna(value):
            return "N/A"
        return f"{value:.2f}{suffix}"

    
    def generate(self, company_id, output_file):

        overview = self.trend.company_overview(company_id)

        if overview.empty:
            raise ValueError(f"No company found for ID {company_id}")

        company = overview.iloc[0]

        company_name = company["company_name"]

        sales = self.trend.sales_trend(company_id)

        profits = self.trend.net_profit_trend(company_id)

        ratios = self.trend.ratio_trend(company_id)

        summary = self.trend.yearly_summary(company_id)

        cashflow = self.trend.cashflow_trend(company_id)

        balance = self.trend.balance_sheet_trend(company_id)

        doc = SimpleDocTemplate(
            str(output_file),
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=20,
        )

        story = []

        header = Table(
            [[company_name]],
            colWidths=[7.2 * inch]
        )

        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTSIZE", (0, 0), (-1, -1), 18),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]))

        story.append(header)
        story.append(Spacer(1, 15))

        latest = summary.iloc[-1] if not summary.empty else pd.Series(dtype=object)
        latest_ratio = ratios.iloc[-1] if not ratios.empty else pd.Series(dtype=object)

        kpi_table = Table(
            [
                ["ROE", self.fmt(company.get("roe_percentage"), "%")],
                ["ROCE", self.fmt(company.get("roce_percentage"), "%")],
                ["Sales", self.fmt(latest.get("sales"))],
                ["Net Profit", self.fmt(latest.get("net_profit"))],
                ["Debt/Equity", self.fmt(latest_ratio.get("debt_to_equity"))],
                ["Quality Score", self.fmt(latest_ratio.get("composite_quality_score"))],
            ],
            colWidths=[2.8 * inch, 3.8 * inch],
        )

        kpi_table.setStyle(TableStyle([

            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

            ("BACKGROUND", (0, 0), (-1, -1),
             colors.whitesmoke),

            ("ALIGN", (0, 0), (-1, -1), "CENTER"),

            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)

        ]))

        story.append(kpi_table)

        story.append(Spacer(1, 20))

        story.append(
            Image(
                self.sales_chart(sales),
                width=6.5 * inch,
                height=3 * inch,
            )
        )

        story.append(Spacer(1, 10))

        story.append(
            Image(
                self.profit_chart(profits),
                width=6.5 * inch,
                height=3 * inch,
            )
        )

        story.append(Spacer(1, 10))

        story.append(
            Image(
                self.roe_chart(ratios),
                width=6.5 * inch,
                height=3 * inch,
            )
        )

        story.append(PageBreak())

        story.append(Paragraph("<b>Balance Sheet Composition</b>", styles["Heading2"]))
        story.append(
            Image(
                self.balance_chart(balance),
                width=6.5 * inch,
                height=3 * inch,
            )
        )

        story.append(Spacer(1, 10))

        story.append(Paragraph("<b>Cash Flow Waterfall</b>", styles["Heading2"]))

        if not cashflow.empty:
            story.append(
                Image(
                    self.cashflow_chart(cashflow.iloc[-1]),
                    width=6.5 * inch,
                    height=3 * inch,
                )
            )
        else:
            story.append(
                Paragraph("Cash flow data not available.", NORMAL)
            )
        story.append(Spacer(1, 12))

        story.append(Paragraph("<font color='green'><b>Pros</b></font>", styles["Heading2"]))

        pros = self.get_pros(company_id)

        if len(pros) == 0:
            story.append(Paragraph("No major strengths available.", NORMAL))
        else:
            for p in pros:
                story.append(
                    Paragraph(
                        f"&#8226; {p}",
                        NORMAL
                    )
                )

        story.append(Spacer(1, 10))

        story.append(Paragraph("<font color='red'><b>Cons</b></font>", styles["Heading2"]))

        cons = self.get_cons(company_id)

        if len(cons) == 0:
            story.append(Paragraph("No major concerns available.", NORMAL))
        else:
            for c in cons:
                story.append(
                    Paragraph(
                        f"&#8226; {c}",
                        NORMAL
                    )
                )

        story.append(Spacer(1, 15))

        label = self.capital_label(company_id)

        badge = Table(
            [[f"Capital Allocation : {label}"]],
            colWidths=[6.5 * inch]
        )

        badge.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), ORANGE),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTSIZE", (0, 0), (-1, -1), 14),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))

        story.append(badge)

        doc.build(story)