import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Peer Comparison",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Peer Comparison")

st.markdown(
    "Compare financial performance of multiple Nifty 100 companies."
)

# -----------------------------------------------------
# DATABASE
# -----------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"


@st.cache_data(ttl=600)
def load_peer_data():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

    c.id,
    c.company_name,

    c.roe_percentage,
    c.roce_percentage,
    c.book_value,

    fr.return_on_equity_pct,
    fr.debt_to_equity,
    fr.interest_coverage,
    fr.free_cash_flow_cr,
    fr.revenue_cagr_5yr,
    fr.pat_cagr_5yr,
    fr.operating_profit_margin_pct,
    fr.composite_quality_score,

    mc.market_cap_crore,
    mc.pe_ratio,
    mc.pb_ratio,
    mc.dividend_yield_pct

    FROM companies c

    LEFT JOIN financial_ratios fr
    ON fr.id = (

        SELECT id

        FROM financial_ratios x

        WHERE x.company_id=c.id

        AND x.return_on_equity_pct IS NOT NULL

        ORDER BY year DESC

        LIMIT 1

    )

    LEFT JOIN market_cap mc

    ON mc.id=(

        SELECT id

        FROM market_cap y

        WHERE y.company_id=c.id

        AND y.pe_ratio IS NOT NULL

        ORDER BY year DESC

        LIMIT 1

    )

    ORDER BY c.company_name
    """

    df = pd.read_sql(query, conn)

    conn.close()

    numeric_cols = [

        "roe_percentage",
        "roce_percentage",
        "book_value",

        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "operating_profit_margin_pct",
        "composite_quality_score",

        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct"

    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_peer_data()

# -----------------------------------------------------
# SIDEBAR
# -----------------------------------------------------

st.sidebar.header("Peer Selection")

companies = sorted(df["company_name"].dropna().unique())

selected = st.sidebar.multiselect(

    "Select Companies",

    companies,

    default=companies[:2]

)

if len(selected) < 2:

    st.warning("Select at least two companies.")

    st.stop()

peer_df = df[df["company_name"].isin(selected)].copy()

peer_df.reset_index(drop=True, inplace=True)

st.subheader("Selected Companies")

st.dataframe(

    peer_df[
        [
            "company_name",
            "market_cap_crore",
            "pe_ratio",
            "pb_ratio"
        ]
    ].round(2),

    use_container_width=True,

    hide_index=True

)

# -----------------------------------------------------
# SUMMARY CARDS
# -----------------------------------------------------

st.divider()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Companies Compared",
    len(peer_df)
)

c2.metric(
    "Highest ROE",
    f"{peer_df['return_on_equity_pct'].max():.2f}%"
)

c3.metric(
    "Largest Market Cap",
    f"₹ {peer_df['market_cap_crore'].max():,.0f} Cr"
)

c4.metric(
    "Best Quality Score",
    f"{peer_df['composite_quality_score'].max():.2f}"
)

st.divider()

# -----------------------------------------------------
# COMPARISON TABLE
# -----------------------------------------------------

comparison = peer_df[
    [
        "company_name",
        "return_on_equity_pct",
        "roce_percentage",
        "debt_to_equity",
        "interest_coverage",
        "free_cash_flow_cr",
        "operating_profit_margin_pct",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct",
        "composite_quality_score"
    ]
].copy()

comparison.columns = [
    "Company",
    "ROE %",
    "ROCE %",
    "Debt/Equity",
    "Interest Coverage",
    "Free Cash Flow",
    "Operating Margin %",
    "Revenue CAGR %",
    "PAT CAGR %",
    "Market Cap (₹ Cr)",
    "P/E",
    "P/B",
    "Dividend Yield %",
    "Quality Score"
]

comparison = comparison.round(2)

st.subheader("Financial Comparison")

st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True,
    height=500
)

# -----------------------------------------------------
# BEST VALUES
# -----------------------------------------------------

st.subheader("Best Performer")

def get_best_company(df, column):
    temp = df.dropna(subset=[column])

    if temp.empty:
        return "N/A"

    return temp.loc[temp[column].idxmax(), "company_name"]


best = pd.DataFrame({

    "Metric": [
        "ROE",
        "ROCE",
        "Revenue CAGR",
        "PAT CAGR",
        "Operating Margin",
        "Quality Score",
        "Dividend Yield"
    ],

    "Company": [

        get_best_company(peer_df, "return_on_equity_pct"),
        get_best_company(peer_df, "roce_percentage"),
        get_best_company(peer_df, "revenue_cagr_5yr"),
        get_best_company(peer_df, "pat_cagr_5yr"),
        get_best_company(peer_df, "operating_profit_margin_pct"),
        get_best_company(peer_df, "composite_quality_score"),
        get_best_company(peer_df, "dividend_yield_pct")

    ]

})

st.dataframe(
    best,
    use_container_width=True,
    hide_index=True
)

# -----------------------------------------------------
# DOWNLOAD
# -----------------------------------------------------

csv = comparison.to_csv(index=False).encode("utf-8")

st.download_button(

    "⬇ Download Comparison",

    csv,

    "peer_comparison.csv",

    "text/csv",

    use_container_width=True

)

st.divider()

# -----------------------------------------------------
# BAR CHART
# -----------------------------------------------------

st.subheader("ROE Comparison")

fig = px.bar(
    peer_df,
    x="company_name",
    y="return_on_equity_pct",
    text="return_on_equity_pct",
    color="company_name"
)

fig.update_layout(
    xaxis_title="Company",
    yaxis_title="ROE (%)",
    showlegend=False,
    height=450
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------
# MARKET CAP
# -----------------------------------------------------

st.subheader("Market Capitalisation")

fig = px.bar(
    peer_df,
    x="company_name",
    y="market_cap_crore",
    color="company_name",
    text="market_cap_crore"
)

fig.update_layout(
    xaxis_title="Company",
    yaxis_title="₹ Crore",
    showlegend=False,
    height=450
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------
# PE VS PB
# -----------------------------------------------------

st.subheader("P/E vs P/B")

fig = px.scatter(
    peer_df,
    x="pe_ratio",
    y="pb_ratio",
    color="company_name",
    size="market_cap_crore",
    hover_name="company_name",
    height=500
)

fig.update_layout(
    xaxis_title="P/E",
    yaxis_title="P/B"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------
# RADAR CHART
# -----------------------------------------------------

st.subheader("Fundamental Radar")

metrics = [

    "return_on_equity_pct",
    "operating_profit_margin_pct",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "interest_coverage",
    "dividend_yield_pct"

]

labels = [

    "ROE",
    "OPM",
    "Revenue CAGR",
    "PAT CAGR",
    "Interest Coverage",
    "Dividend Yield"

]

fig = go.Figure()

for _, row in peer_df.iterrows():

    values = []

    for metric in metrics:
        values.append(
            0 if pd.isna(row[metric]) else row[metric]
        )

    values.append(values[0])

    fig.add_trace(

        go.Scatterpolar(

            r=values,

            theta=labels + [labels[0]],

            fill="toself",

            name=row["company_name"]

        )

    )

fig.update_layout(

    polar=dict(radialaxis=dict(visible=True)),

    showlegend=True,

    height=650

)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------
# QUALITY SCORE
# -----------------------------------------------------

st.subheader("Composite Quality Score")

quality = peer_df[
    [
        "company_name",
        "composite_quality_score"
    ]
].sort_values(
    "composite_quality_score",
    ascending=False
)

fig = px.bar(

    quality,

    x="company_name",

    y="composite_quality_score",

    text="composite_quality_score",

    color="company_name"

)

fig.update_layout(

    showlegend=False,

    height=450,

    xaxis_title="Company",

    yaxis_title="Quality Score"

)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------
# FINAL SUMMARY
# -----------------------------------------------------

st.divider()

st.success(
    "Peer comparison completed successfully."
)

st.caption(
    "Data shown corresponds to the latest available financial information for each company."
)