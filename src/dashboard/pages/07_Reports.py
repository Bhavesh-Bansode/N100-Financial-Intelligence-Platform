import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import plotly.express as px

st.set_page_config(
    page_title="Reports",
    page_icon="📑",
    layout="wide"
)

st.title("📑 Financial Reports")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"


@st.cache_data(ttl=600)
def load_reports():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        c.company_name,

        p.sales,
        p.expenses,
        p.operating_profit,
        p.opm_percentage,
        p.profit_before_tax,
        p.net_profit,
        p.eps,
        p.dividend_payout,

        b.equity_capital,
        b.reserves,
        b.borrowings,
        b.total_assets,
        b.total_liabilities,

        cf.operating_activity,
        cf.investing_activity,
        cf.financing_activity,
        cf.net_cash_flow,

        fr.return_on_equity_pct,
        fr.operating_profit_margin_pct,

        mc.market_cap_crore,
        mc.pe_ratio,
        mc.pb_ratio,
        mc.dividend_yield_pct

    FROM companies c

    LEFT JOIN profitandloss p

    ON p.id=(

        SELECT id

        FROM profitandloss

        WHERE company_id=c.id

        ORDER BY year DESC

        LIMIT 1

    )

    LEFT JOIN balancesheet b

    ON b.id=(

        SELECT id

        FROM balancesheet

        WHERE company_id=c.id

        ORDER BY year DESC

        LIMIT 1

    )

    LEFT JOIN cashflow cf

    ON cf.id=(

        SELECT id

        FROM cashflow

        WHERE company_id=c.id

        ORDER BY year DESC

        LIMIT 1

    )

    LEFT JOIN financial_ratios fr

    ON fr.id=(

        SELECT id

        FROM financial_ratios

        WHERE company_id=c.id

        ORDER BY year DESC

        LIMIT 1

    )

    LEFT JOIN market_cap mc

    ON mc.id=(

        SELECT id

        FROM market_cap

        WHERE company_id=c.id

        ORDER BY year DESC

        LIMIT 1

    )

    ORDER BY c.company_name
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


df = load_reports()

companies = sorted(df.company_name.unique())

company = st.sidebar.selectbox(

    "Select Company",

    companies

)

report = df[df.company_name == company]

st.subheader(company)

st.dataframe(

    report,

    use_container_width=True,

    hide_index=True

)
# ---------------------------------------------------------
# KEY METRICS
# ---------------------------------------------------------

st.divider()

c1, c2, c3, c4 = st.columns(4)

sales = report["sales"].iloc[0]
profit = report["net_profit"].iloc[0]
roe = report["return_on_equity_pct"].iloc[0]
pe = report["pe_ratio"].iloc[0]

c1.metric(
    "Sales",
    f"₹ {sales:,.2f} Cr" if pd.notna(sales) else "N/A"
)

c2.metric(
    "Net Profit",
    f"₹ {profit:,.2f} Cr" if pd.notna(profit) else "N/A"
)

c3.metric(
    "ROE",
    f"{roe:.2f} %" if pd.notna(roe) else "N/A"
)

c4.metric(
    "P/E",
    f"{pe:.2f}" if pd.notna(pe) else "N/A"
)

st.divider()

# ---------------------------------------------------------
# PROFIT & LOSS
# ---------------------------------------------------------

st.subheader("📈 Profit & Loss")

pl = pd.DataFrame({

    "Metric":[
        "Sales",
        "Expenses",
        "Operating Profit",
        "Operating Margin %",
        "Profit Before Tax",
        "Net Profit",
        "EPS",
        "Dividend Payout"
    ],

    "Value":[
        report["sales"].iloc[0],
        report["expenses"].iloc[0],
        report["operating_profit"].iloc[0],
        report["opm_percentage"].iloc[0],
        report["profit_before_tax"].iloc[0],
        report["net_profit"].iloc[0],
        report["eps"].iloc[0],
        report["dividend_payout"].iloc[0]
    ]

})

st.dataframe(
    pl.round(2),
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------------
# BALANCE SHEET
# ---------------------------------------------------------

st.subheader("🏦 Balance Sheet")

bs = pd.DataFrame({

    "Metric":[
        "Equity Capital",
        "Reserves",
        "Borrowings",
        "Total Assets",
        "Total Liabilities"
    ],

    "Value":[
        report["equity_capital"].iloc[0],
        report["reserves"].iloc[0],
        report["borrowings"].iloc[0],
        report["total_assets"].iloc[0],
        report["total_liabilities"].iloc[0]
    ]

})

st.dataframe(
    bs.round(2),
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------------
# CASH FLOW
# ---------------------------------------------------------

st.subheader("💰 Cash Flow")

cf = pd.DataFrame({

    "Metric":[
        "Operating Activity",
        "Investing Activity",
        "Financing Activity",
        "Net Cash Flow"
    ],

    "Value":[
        report["operating_activity"].iloc[0],
        report["investing_activity"].iloc[0],
        report["financing_activity"].iloc[0],
        report["net_cash_flow"].iloc[0]
    ]

})

st.dataframe(
    cf.round(2),
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------------
# FINANCIAL RATIOS
# ---------------------------------------------------------

st.subheader("📊 Financial Ratios")

ratios = pd.DataFrame({

    "Metric":[
        "ROE %",
        "Operating Margin %",
        "Market Cap (₹ Cr)",
        "P/E",
        "P/B",
        "Dividend Yield %"
    ],

    "Value":[
        report["return_on_equity_pct"].iloc[0],
        report["operating_profit_margin_pct"].iloc[0],
        report["market_cap_crore"].iloc[0],
        report["pe_ratio"].iloc[0],
        report["pb_ratio"].iloc[0],
        report["dividend_yield_pct"].iloc[0]
    ]

})

st.dataframe(
    ratios.round(2),
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------------
# DOWNLOAD REPORT
# ---------------------------------------------------------

csv = report.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Download Report",
    csv,
    f"{company}_report.csv",
    "text/csv",
    use_container_width=True
)

st.divider()

st.success("Financial report generated successfully.")