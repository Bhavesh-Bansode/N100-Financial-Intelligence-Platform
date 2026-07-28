import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from io import BytesIO

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Stock Screener",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Nifty 100 Stock Screener")
st.markdown(
    "Filter companies using fundamental metrics. "
    "Results update automatically as filters change."
)

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DB_PATH = PROJECT_ROOT / "data" / "nifty100.db"

print("Database Path:", DB_PATH)
print("Exists:", DB_PATH.exists())

@st.cache_data(ttl=600)
def load_data():
    
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        c.id,
        c.company_name,

        fr.year,
        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.free_cash_flow_cr,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.operating_profit_margin_pct,
        fr.interest_coverage,
        fr.composite_quality_score,

        mc.market_cap_crore,
        mc.pe_ratio,
        mc.pb_ratio,
        mc.dividend_yield_pct

    FROM companies c

    LEFT JOIN financial_ratios fr
    ON fr.id = (
        SELECT id
        FROM financial_ratios f2
        WHERE f2.company_id = c.id
        AND f2.return_on_equity_pct IS NOT NULL
        ORDER BY year DESC
        LIMIT 1
    )

    LEFT JOIN market_cap mc
    ON mc.id = (
        SELECT id
        FROM market_cap m2
        WHERE m2.company_id = c.id
        AND m2.pe_ratio IS NOT NULL
        ORDER BY year DESC
        LIMIT 1
    )
    """
    df = pd.read_sql(query, conn)

    conn.close()

    numeric_cols = [
        "return_on_equity_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "operating_profit_margin_pct",
        "interest_coverage",
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct",
        "composite_quality_score"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_data()

st.write(df.isnull().sum())

# --------------------------------------------------
# PRESET FILTERS
# --------------------------------------------------

PRESETS = {

    "Quality": {
        "roe": 18,
        "de": 1.0,
        "fcf": 0,
        "rev": 10,
        "pat": 10,
        "opm": 15,
        "pe": 80,
        "pb": 15,
        "div": 0,
        "icr": 5
    },

    "Value": {
        "roe": 10,
        "de": 2,
        "fcf": -10000,
        "rev": -50,
        "pat": -50,
        "opm": 0,
        "pe": 20,
        "pb": 3,
        "div": 0,
        "icr": 2
    },

    "Growth": {
        "roe": 15,
        "de": 2,
        "fcf": 0,
        "rev": 15,
        "pat": 15,
        "opm": 15,
        "pe": 100,
        "pb": 20,
        "div": 0,
        "icr": 3
    },

    "Dividend": {
        "roe": 10,
        "de": 2,
        "fcf": 0,
        "rev": 0,
        "pat": 0,
        "opm": 5,
        "pe": 80,
        "pb": 10,
        "div": 2,
        "icr": 2
    },

    "Debt-Free": {
        "roe": 10,
        "de": 0.10,
        "fcf": 0,
        "rev": 0,
        "pat": 0,
        "opm": 5,
        "pe": 80,
        "pb": 15,
        "div": 0,
        "icr": 5
    },

    "Turnaround": {
        "roe": 0,
        "de": 3,
        "fcf": -10000,
        "rev": 5,
        "pat": 5,
        "opm": 0,
        "pe": 100,
        "pb": 10,
        "div": 0,
        "icr": 1
    }

}

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("Screening Presets")

preset = st.sidebar.radio(
    "Choose Preset",
    [
        "Custom",
        "Quality",
        "Value",
        "Growth",
        "Dividend",
        "Debt-Free",
        "Turnaround"
    ]
)

if preset == "Custom":
    defaults = {
        "roe": 0,
        "de": 10,
        "fcf": -10000,
        "rev": -50,
        "pat": -50,
        "opm": -50,
        "pe": 200,
        "pb": 50,
        "div": 0,
        "icr": 0
    }
else:
    defaults = PRESETS[preset]

st.sidebar.header("Filters")

roe_min = st.sidebar.slider(
    "Minimum ROE (%)",
    0.0,
    50.0,
    float(defaults["roe"]),
    0.5
)

de_max = st.sidebar.slider(
    "Maximum Debt/Equity",
    0.0,
    10.0,
    float(defaults["de"]),
    0.1
)

fcf_min = st.sidebar.slider(
    "Minimum Free Cash Flow (₹ Cr)",
    -10000,
    50000,
    int(defaults["fcf"]),
    100
)

rev_min = st.sidebar.slider(
    "Minimum Revenue CAGR (%)",
    -50,
    50,
    int(defaults["rev"])
)

pat_min = st.sidebar.slider(
    "Minimum PAT CAGR (%)",
    -50,
    50,
    int(defaults["pat"])
)

opm_min = st.sidebar.slider(
    "Minimum Operating Margin (%)",
    -20,
    60,
    int(defaults["opm"])
)

pe_max = st.sidebar.slider(
    "Maximum P/E",
    0,
    200,
    int(defaults["pe"])
)

pb_max = st.sidebar.slider(
    "Maximum P/B",
    0,
    50,
    int(defaults["pb"])
)

div_min = st.sidebar.slider(
    "Minimum Dividend Yield (%)",
    0.0,
    10.0,
    float(defaults["div"]),
    0.1
)

icr_min = st.sidebar.slider(
    "Minimum Interest Coverage",
    0,
    30,
    int(defaults["icr"])
)

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df.copy()

filtered_df = filtered_df[
    (
        filtered_df["return_on_equity_pct"].fillna(-999)
        >= roe_min
    )
]

filtered_df = filtered_df[
    (
        filtered_df["debt_to_equity"].fillna(999)
        <= de_max
    )
]

filtered_df = filtered_df[
    (
        filtered_df["free_cash_flow_cr"].fillna(-999999)
        >= fcf_min
    )
]

filtered_df = filtered_df[
    (
        filtered_df["revenue_cagr_5yr"].fillna(-999)
        >= rev_min
    )
]

filtered_df = filtered_df[
    (
        filtered_df["pat_cagr_5yr"].fillna(-999)
        >= pat_min
    )
]

filtered_df = filtered_df[
    (
        filtered_df["operating_profit_margin_pct"].fillna(-999)
        >= opm_min
    )
]

filtered_df = filtered_df[
    (
        filtered_df["pe_ratio"].fillna(999)
        <= pe_max
    )
]

filtered_df = filtered_df[
    (
        filtered_df["pb_ratio"].fillna(999)
        <= pb_max
    )
]

filtered_df = filtered_df[
    (
        filtered_df["dividend_yield_pct"].fillna(-999)
        >= div_min
    )
]

filtered_df = filtered_df[
    (
        filtered_df["interest_coverage"].fillna(-999)
        >= icr_min
    )
]

# --------------------------------------------------
# SORT RESULTS
# --------------------------------------------------

filtered_df = filtered_df.sort_values(
    by="composite_quality_score",
    ascending=False,
    na_position="last"
).reset_index(drop=True)

# --------------------------------------------------
# KPI SUMMARY
# --------------------------------------------------

st.markdown("## Screening Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Matching Companies",
    len(filtered_df)
)

c2.metric(
    "Average ROE",
    f"{filtered_df['return_on_equity_pct'].mean():.2f}%"
    if len(filtered_df)
    else "N/A"
)

c3.metric(
    "Median P/E",
    f"{filtered_df['pe_ratio'].median():.2f}"
    if len(filtered_df)
    else "N/A"
)

c4.metric(
    "Average Quality Score",
    f"{filtered_df['composite_quality_score'].mean():.2f}"
    if len(filtered_df)
    else "N/A"
)

st.divider()

# --------------------------------------------------
# RESULT COUNT
# --------------------------------------------------

st.subheader(
    f"{len(filtered_df)} companies match your filters"
)

if filtered_df.empty:

    st.warning(
        "No companies satisfy the selected filters.\n\n"
        "Try relaxing one or more conditions."
    )

    st.stop()

# --------------------------------------------------
# DISPLAY TABLE
# --------------------------------------------------

display_df = filtered_df[
    [
        "id",
        "company_name",
        "return_on_equity_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "operating_profit_margin_pct",
        "interest_coverage",
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct",
        "composite_quality_score",
    ]
].copy()

display_df.columns = [
    "Ticker",
    "Company",
    "ROE %",
    "Debt/Equity",
    "FCF (₹ Cr)",
    "Revenue CAGR %",
    "PAT CAGR %",
    "OPM %",
    "Interest Coverage",
    "Market Cap (₹ Cr)",
    "P/E",
    "P/B",
    "Dividend Yield %",
    "Quality Score",
]

numeric_cols = display_df.select_dtypes(include="number").columns

display_df[numeric_cols] = display_df[numeric_cols].round(2)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    height=650
)

# --------------------------------------------------
# DOWNLOAD CSV
# --------------------------------------------------

csv = display_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Results as CSV",
    data=csv,
    file_name="nifty100_screener_results.csv",
    mime="text/csv",
    use_container_width=True,
)

# --------------------------------------------------
# TOP QUALITY COMPANIES
# --------------------------------------------------

st.divider()

st.subheader("🏆 Top 10 Companies by Composite Quality Score")

top10 = (
    filtered_df[
        [
            "company_name",
            "composite_quality_score",
            "return_on_equity_pct",
            "pe_ratio",
            "pb_ratio",
            "dividend_yield_pct",
        ]
    ]
    .sort_values(
        "composite_quality_score",
        ascending=False
    )
    .head(10)
    .reset_index(drop=True)
)

top10.columns = [
    "Company",
    "Quality Score",
    "ROE %",
    "P/E",
    "P/B",
    "Dividend Yield %",
]

top10 = top10.round(2)

st.dataframe(
    top10,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.caption(
    "Filters are applied on the latest available financial year "
    "for each company. Missing values are safely ignored where "
    "possible to prevent application crashes."
)