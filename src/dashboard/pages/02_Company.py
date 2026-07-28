import streamlit as st
import pandas as pd

from dashboard.utils.db import db
from dashboard.utils.charts import ChartBuilder
from analytics.trends import trend
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SETTINGS_FILE = PROJECT_ROOT / "src" / "dashboard" / "config" / "settings.json"

with open(SETTINGS_FILE, "r") as f:
    settings = json.load(f)
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SETTINGS_FILE = PROJECT_ROOT / "src" / "dashboard" / "config" / "settings.json"

with open(SETTINGS_FILE, "r") as f:
    settings = json.load(f)

st.set_page_config(
    page_title="Company Analysis",
    layout="wide"
)

st.title("🏢 Company Analysis")

st.markdown("---")

# ---------------------------------------------------
# Load Company List
# ---------------------------------------------------

companies = db.fetch_dataframe(
    """
    SELECT
        id,
        company_name
    FROM companies
    ORDER BY company_name
    """
)

company_name = st.selectbox(
    "Select Company",
    companies["company_name"]
)

company_id = companies.loc[
    companies["company_name"] == company_name,
    "id"
].iloc[0]

overview = trend.company_overview(company_id)

if overview.empty:
    st.error("Company information not available.")
    st.stop()

overview = overview.iloc[0]

st.header(overview["company_name"])

col1, col2 = st.columns([1,3])

with col1:

    logo = overview["company_logo"]

    if pd.notna(logo) and str(logo).strip() != "":
        st.image(logo, width=120)
    else:
        st.info("Logo not available")

with col2:

    st.markdown(
        f"### {overview['company_name']}"
    )

    st.write(
        overview["about_company"]
    )

    st.write(
        f"**Website:** {overview['website']}"
    )
    st.write(f"🌐 Website : {overview['website']}")
    st.write(f"📊 NSE Profile : {overview['nse_profile']}")
    st.write(f"📈 BSE Profile : {overview['bse_profile']}")

st.markdown("---")

st.subheader("Basic Information")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Book Value",
    round(
        overview["book_value"],
        2
    )
)

c2.metric(
    "Face Value",
    round(
        overview["face_value"],
        2
    )
)

c3.metric(
    "ROE (%)",
    round(
        overview["roe_percentage"],
        2
    )
)

c4.metric(
    "ROCE (%)",
    round(
        overview["roce_percentage"],
        2
    )
)

st.markdown("---")

st.subheader("Sector Details")

left, right = st.columns(2)

left.info(
    f"Broad Sector : {overview['broad_sector']}"
)

right.info(
    f"Sub Sector : {overview['sub_sector']}"
)

st.success(
    f"Market Cap Category : {overview['market_cap_category']}"
)

st.markdown("---")

# ==========================================================
# FINANCIAL STATEMENTS
# ==========================================================

st.header("Financial Statements")

tab1, tab2, tab3 = st.tabs(
    [
        "Profit & Loss",
        "Balance Sheet",
        "Cash Flow"
    ]
)

# ----------------------------------------------------------
# PROFIT & LOSS
# ----------------------------------------------------------

with tab1:

    pnl = db.fetch_dataframe(
        """
        SELECT
            year,
            sales,
            expenses,
            operating_profit,
            opm_percentage,
            other_income,
            interest,
            depreciation,
            profit_before_tax,
            tax_percentage,
            net_profit,
            eps,
            dividend_payout
        FROM profitandloss
        WHERE company_id=?
        ORDER BY year
        """,
        (company_id,)
    )

    if pnl.empty:

        st.warning("No Profit & Loss data available.")

    else:

        st.dataframe(
            pnl,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        c1, c2 = st.columns(2)

        with c1:

            fig = ChartBuilder.line_chart(
                pnl,
                "year",
                "sales",
                title="Sales Trend",
                xlabel="Year",
                ylabel="Sales"
            )

            st.pyplot(fig)

        with c2:

            fig = ChartBuilder.line_chart(
                pnl,
                "year",
                "net_profit",
                title="Net Profit Trend",
                xlabel="Year",
                ylabel="Net Profit"
            )

            st.pyplot(fig)

# ----------------------------------------------------------
# BALANCE SHEET
# ----------------------------------------------------------

with tab2:

    bs = db.fetch_dataframe(
        """
        SELECT
            year,
            equity_capital,
            reserves,
            borrowings,
            other_liabilities,
            total_liabilities,
            fixed_assets,
            cwip,
            investments,
            other_asset,
            total_assets
        FROM balancesheet
        WHERE company_id=?
        ORDER BY year
        """,
        (company_id,)
    )

    if bs.empty:

        st.warning("No Balance Sheet data available.")

    else:

        st.dataframe(
            bs,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        c1, c2 = st.columns(2)

        with c1:

            fig = ChartBuilder.line_chart(
                bs,
                "year",
                "total_assets",
                title="Total Assets",
                xlabel="Year",
                ylabel="Assets"
            )

            st.pyplot(fig)

        with c2:

            fig = ChartBuilder.line_chart(
                bs,
                "year",
                "borrowings",
                title="Borrowings",
                xlabel="Year",
                ylabel="Borrowings"
            )

            st.pyplot(fig)

# ----------------------------------------------------------
# CASH FLOW
# ----------------------------------------------------------

with tab3:

    cf = db.fetch_dataframe(
        """
        SELECT
            year,
            operating_activity,
            investing_activity,
            financing_activity,
            net_cash_flow
        FROM cashflow
        WHERE company_id=?
        ORDER BY year
        """,
        (company_id,)
    )

    if cf.empty:

        st.warning("No Cash Flow data available.")

    else:

        st.dataframe(
            cf,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        c1, c2 = st.columns(2)

        with c1:

            fig = ChartBuilder.line_chart(
                cf,
                "year",
                "operating_activity",
                title="Operating Cash Flow",
                xlabel="Year",
                ylabel="Operating Cash Flow"
            )

            st.pyplot(fig)

        with c2:

            fig = ChartBuilder.line_chart(
                cf,
                "year",
                "net_cash_flow",
                title="Net Cash Flow",
                xlabel="Year",
                ylabel="Net Cash Flow"
            )

            st.pyplot(fig)

st.markdown("---")

# ==========================================================
# STOCK PRICE HISTORY
# ==========================================================

st.header("Stock Price History")

price_df = db.fetch_dataframe(
    """
    SELECT
        date,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        adjusted_close
    FROM stock_prices
    WHERE company_id = ?
    ORDER BY date
    """,
    (company_id,)
)

if price_df.empty:

    st.warning("Stock price history not available.")

else:

    st.dataframe(
        price_df.tail(30),
        use_container_width=True,
        hide_index=True
    )

    fig = ChartBuilder.line_chart(
        price_df,
        "date",
        "close_price",
        title="Closing Price Trend",
        xlabel="Date",
        ylabel="Closing Price"
    )

    st.pyplot(fig)

st.markdown("---")

# ==========================================================
# PROS & CONS
# ==========================================================

st.header("Pros & Cons")
pros_cons = db.fetch_dataframe(
    """
    SELECT
        pros,
        cons
    FROM prosandcons
    WHERE company_id=?
    """,
    (company_id,)
)

if pros_cons.empty:

    st.info("Pros & Cons not available.")

else:

    left, right = st.columns(2)

    with left:

        st.subheader("✅ Pros")

        for value in pros_cons["pros"].dropna():

            st.success(value)

    with right:

        st.subheader("⚠ Cons")

        for value in pros_cons["cons"].dropna():

            st.error(value)

st.markdown("---")

# ==========================================================
# DOCUMENTS
# ==========================================================

st.header("Company Documents")

docs = db.fetch_dataframe(
    """
    SELECT
        Year,
        Annual_Report
    FROM documents
    WHERE company_id = ?
    ORDER BY Year DESC
    """,
    (company_id,)
)

if docs.empty:

    st.info("No documents available.")

else:

    doc = docs.iloc[0]

    if docs.empty:
        st.info("No annual reports available.")
    else:
        st.dataframe(docs, use_container_width=True, hide_index=True)

        latest = docs.iloc[0]

        st.link_button(
            "📄 Latest Annual Report",
            latest["Annual_Report"]
        )

st.markdown("---")

# ==========================================================
# FINANCIAL RATIOS
# ==========================================================

ratio_df = db.fetch_dataframe(
    """
    SELECT *
    FROM financial_ratios
    WHERE company_id = ?
    ORDER BY year
    """,
    (company_id,)
)

# ==========================================================
# DASHBOARD SUMMARY
# ==========================================================
valuation = db.fetch_dataframe(
    """
    SELECT
        year,
        market_cap_crore
    FROM market_cap
    WHERE company_id = ?
    ORDER BY year
    """,
    (company_id,)
)
st.header("Company Snapshot")

summary_col1, summary_col2 = st.columns(2)

with summary_col1:

    st.metric(
        "Latest Market Cap",
        f"{valuation.iloc[-1]['market_cap_crore']:,.2f}"
        if not valuation.empty else "-"
    )

    st.metric(
        "Latest ROE (%)",
        round(
            ratio_df.iloc[-1]["return_on_equity_pct"],
            2
        )
        if not ratio_df.empty else "-"
    )

    st.metric(
        "Latest EPS",
        round(
            ratio_df.iloc[-1]["earnings_per_share"],
            2
        )
        if not ratio_df.empty else "-"
    )

with summary_col2:

    st.metric(
        "Book Value",
        round(
            overview["book_value"],
            2
        )
    )

    st.metric(
        "Face Value",
        round(
            overview["face_value"],
            2
        )
    )

    if not ratio_df.empty:

        score = ratio_df.iloc[-1]["composite_quality_score"]

        if pd.notna(score):

            if score >= 80:

                st.success(f"Excellent Quality Score : {score:.2f}")

            elif score >= 60:

                st.info(f"Good Quality Score : {score:.2f}")

            elif score >= 40:

                st.warning(f"Average Quality Score : {score:.2f}")

            else:

                st.error(f"Weak Quality Score : {score:.2f}")

st.markdown("---")

st.success("Company dashboard loaded successfully.")