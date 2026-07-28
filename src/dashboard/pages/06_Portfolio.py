import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import plotly.express as px

st.set_page_config(
    page_title="Portfolio",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Portfolio Tracker")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"


@st.cache_data(ttl=600)
def load_data():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        c.id,
        c.company_name,

        mc.market_cap_crore,
        mc.pe_ratio,
        mc.pb_ratio,
        mc.dividend_yield_pct,

        fr.return_on_equity_pct,
        fr.operating_profit_margin_pct,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.composite_quality_score

    FROM companies c

    LEFT JOIN market_cap mc

    ON mc.id=(

        SELECT id

        FROM market_cap

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

    ORDER BY c.company_name
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


df = load_data()

companies = sorted(df.company_name.unique())

st.sidebar.header("Portfolio Builder")

selected = st.sidebar.multiselect(

    "Select Companies",

    companies

)

if len(selected) == 0:

    st.info("Select companies from sidebar.")

    st.stop()

portfolio = df[df.company_name.isin(selected)].copy()

st.subheader("Portfolio Holdings")

portfolio["Investment (₹)"] = 100000

portfolio["Weight %"] = (
    portfolio["Investment (₹)"] /
    portfolio["Investment (₹)"].sum()
) * 100

st.dataframe(

    portfolio[
        [
            "company_name",
            "Investment (₹)",
            "Weight %",
            "market_cap_crore",
            "pe_ratio",
            "return_on_equity_pct"
        ]
    ].round(2),

    hide_index=True,

    use_container_width=True

)

# ---------------------------------------------------------
# PORTFOLIO SUMMARY
# ---------------------------------------------------------

st.divider()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Companies",
    len(portfolio)
)

c2.metric(
    "Investment",
    f"₹ {portfolio['Investment (₹)'].sum():,.0f}"
)

c3.metric(
    "Average ROE",
    f"{portfolio['return_on_equity_pct'].mean():.2f}%"
)

c4.metric(
    "Average P/E",
    f"{portfolio['pe_ratio'].mean():.2f}"
)

st.divider()

# ---------------------------------------------------------
# WEIGHT CHART
# ---------------------------------------------------------

st.subheader("Portfolio Allocation")

fig = px.pie(

    portfolio,

    names="company_name",

    values="Investment (₹)",

    hole=0.45

)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# MARKET CAP DISTRIBUTION
# ---------------------------------------------------------

st.subheader("Market Capitalisation")

fig = px.bar(

    portfolio,

    x="company_name",

    y="market_cap_crore",

    color="company_name",

    text="market_cap_crore"

)

fig.update_layout(

    showlegend=False,

    height=450,

    xaxis_title="Company",

    yaxis_title="₹ Crore"

)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# ROE COMPARISON
# ---------------------------------------------------------

st.subheader("ROE Comparison")

fig = px.bar(

    portfolio,

    x="company_name",

    y="return_on_equity_pct",

    color="company_name",

    text="return_on_equity_pct"

)

fig.update_layout(

    showlegend=False,

    height=450,

    xaxis_title="Company",

    yaxis_title="ROE (%)"

)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# PORTFOLIO QUALITY
# ---------------------------------------------------------

st.subheader("Portfolio Quality")

quality = portfolio[

    [

        "company_name",

        "composite_quality_score"

    ]

].sort_values(

    "composite_quality_score",

    ascending=False

)

st.dataframe(

    quality.round(2),

    hide_index=True,

    use_container_width=True

)

# ---------------------------------------------------------
# DOWNLOAD
# ---------------------------------------------------------

csv = portfolio.to_csv(index=False).encode("utf-8")

st.download_button(

    "📥 Download Portfolio",

    csv,

    "portfolio.csv",

    "text/csv",

    use_container_width=True

)

st.divider()

