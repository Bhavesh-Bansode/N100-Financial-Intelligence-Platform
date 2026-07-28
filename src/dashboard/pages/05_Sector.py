import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import plotly.express as px

st.set_page_config(
    page_title="Sector Analysis",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 Sector Analysis")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"


@st.cache_data(ttl=600)
def load_sector_data():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        c.id,
        c.company_name,

        s.broad_sector,
        s.sub_sector,
        s.market_cap_category,
        s.index_weight_pct,

        fr.return_on_equity_pct,
        fr.operating_profit_margin_pct,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.debt_to_equity,
        fr.interest_coverage,
        fr.composite_quality_score,

        mc.market_cap_crore,
        mc.pe_ratio,
        mc.pb_ratio,
        mc.dividend_yield_pct

    FROM companies c

    LEFT JOIN sectors s

        ON c.id=s.company_id

    LEFT JOIN financial_ratios fr

        ON fr.id=(

            SELECT id

            FROM financial_ratios f

            WHERE f.company_id=c.id

            ORDER BY year DESC

            LIMIT 1

        )

    LEFT JOIN market_cap mc

        ON mc.id=(

            SELECT id

            FROM market_cap m

            WHERE m.company_id=c.id

            ORDER BY year DESC

            LIMIT 1

        )

    ORDER BY c.company_name
    """

    df = pd.read_sql(query, conn)

    conn.close()

    numeric = [

        "return_on_equity_pct",
        "operating_profit_margin_pct",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "debt_to_equity",
        "interest_coverage",
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct",
        "composite_quality_score"

    ]

    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_sector_data()

st.sidebar.header("Sector Filter")

sector_list = sorted(df["broad_sector"].dropna().unique())

selected_sector = st.sidebar.selectbox(
    "Select Sector",
    sector_list
)

sector_df = df[df["broad_sector"] == selected_sector].copy()

st.subheader(selected_sector)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Companies",
    len(sector_df)
)

c2.metric(
    "Average ROE",
    f"{sector_df['return_on_equity_pct'].mean():.2f}%"
)

c3.metric(
    "Average P/E",
    f"{sector_df['pe_ratio'].mean():.2f}"
)

c4.metric(
    "Market Cap",
    f"₹ {sector_df['market_cap_crore'].sum():,.0f} Cr"
)

st.divider()

st.dataframe(

    sector_df[

        [

            "company_name",
            "sub_sector",
            "market_cap_category",
            "index_weight_pct",
            "return_on_equity_pct",
            "market_cap_crore",
            "pe_ratio",
            "pb_ratio",
            "dividend_yield_pct"

        ]

    ],

    use_container_width=True,

    hide_index=True

)

# ---------------------------------------------------------
# TOP COMPANIES
# ---------------------------------------------------------

st.subheader("🏆 Top Companies")

top = sector_df.sort_values(
    "market_cap_crore",
    ascending=False
).head(10)

st.dataframe(

    top[
        [
            "company_name",
            "market_cap_crore",
            "return_on_equity_pct",
            "pe_ratio",
            "pb_ratio",
            "composite_quality_score"
        ]
    ].round(2),

    hide_index=True,
    use_container_width=True

)

# ---------------------------------------------------------
# MARKET CAP CHART
# ---------------------------------------------------------

st.subheader("Market Capitalisation")

fig = px.bar(

    top,

    x="company_name",

    y="market_cap_crore",

    color="company_name",

    text="market_cap_crore"

)

fig.update_layout(

    showlegend=False,

    xaxis_title="Company",

    yaxis_title="Market Cap (₹ Cr)",

    height=500

)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# ROE CHART
# ---------------------------------------------------------

st.subheader("Return on Equity")

roe = sector_df.sort_values(
    "return_on_equity_pct",
    ascending=False
)

fig = px.bar(

    roe,

    x="company_name",

    y="return_on_equity_pct",

    color="company_name",

    text="return_on_equity_pct"

)

fig.update_layout(

    showlegend=False,

    height=500,

    xaxis_title="Company",

    yaxis_title="ROE (%)"

)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# PE VS PB
# ---------------------------------------------------------

st.subheader("P/E vs P/B")

fig = px.scatter(

    sector_df,

    x="pe_ratio",

    y="pb_ratio",

    size="market_cap_crore",

    color="company_name",

    hover_name="company_name",

    height=550

)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# QUALITY SCORE
# ---------------------------------------------------------

st.subheader("Quality Score Ranking")

quality = sector_df.sort_values(
    "composite_quality_score",
    ascending=False
)

fig = px.bar(

    quality,

    x="company_name",

    y="composite_quality_score",

    color="company_name",

    text="composite_quality_score"

)

fig.update_layout(

    showlegend=False,

    height=500,

    xaxis_title="Company",

    yaxis_title="Quality Score"

)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# SECTOR STATISTICS
# ---------------------------------------------------------

st.subheader("Sector Statistics")

stats = pd.DataFrame({

    "Metric": [

        "Average ROE",
        "Average P/E",
        "Average P/B",
        "Average Dividend Yield",
        "Average Revenue CAGR",
        "Average PAT CAGR",
        "Average OPM",
        "Average Debt/Equity"

    ],

    "Value": [

        round(sector_df["return_on_equity_pct"].mean(),2),
        round(sector_df["pe_ratio"].mean(),2),
        round(sector_df["pb_ratio"].mean(),2),
        round(sector_df["dividend_yield_pct"].mean(),2),
        round(sector_df["revenue_cagr_5yr"].mean(),2),
        round(sector_df["pat_cagr_5yr"].mean(),2),
        round(sector_df["operating_profit_margin_pct"].mean(),2),
        round(sector_df["debt_to_equity"].mean(),2)

    ]

})

st.dataframe(

    stats,

    hide_index=True,

    use_container_width=True

)

# ---------------------------------------------------------
# DOWNLOAD
# ---------------------------------------------------------

csv = sector_df.to_csv(index=False).encode("utf-8")

st.download_button(

    "📥 Download Sector Data",

    csv,

    f"{selected_sector}_sector.csv",

    "text/csv",

    use_container_width=True

)

st.divider()

st.success("Sector analysis completed.")