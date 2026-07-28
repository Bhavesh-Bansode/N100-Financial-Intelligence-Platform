# Nifty 100 Financial Intelligence Platform

A financial analytics platform for 92 Nifty 100 companies built using Python, SQLite, Pandas, Plotly, and Streamlit. The platform provides company analysis, stock screening, peer comparison, sector insights, valuation analytics, and interactive dashboards using historical financial data.

---

## Features

- Company Profile Dashboard
- Stock Screener
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation Analysis
- Annual Reports Viewer
- Valuation Analysis
- Composite Quality Score
- Sector Relative Score
- Interactive Plotly Charts
- CSV and Excel Export

---

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- SQLite
- OpenPyXL
- YAML

---

## Project Structure

```
data/
│
├── supporting/
│
output/
│
├── valuation_summary.xlsx
├── valuation_flags.csv
├── pe_trend.xlsx
├── pb_vs_roe.xlsx
├── ev_ebitda_comparison.xlsx
└── dividend_yield_ranker.xlsx
│
src/
│
├── analytics/
├── dashboard/
│   ├── pages/
│   └── utils/
│
config/

requirements.txt
README.md
```

---

## Installation

Create a virtual environment

```bash
python -m venv .venv
```

Activate the virtual environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install the required packages

```bash
pip install -r requirements.txt
```

---

## Run Dashboard

```bash
streamlit run src/dashboard/app.py
```

---

## Dashboard Modules

### Home
- Project overview
- Key financial KPIs
- Sector distribution
- Market overview

### Company Profile
- Company information
- Financial metrics
- Historical performance
- Interactive charts

### Stock Screener
- Multi-parameter filtering
- Financial ratio screening
- CSV export

### Peer Comparison
- Compare companies within a sector
- Radar chart visualization
- Financial metric comparison

### Trend Analysis
- Historical trends
- Revenue, Profit, ROE and other financial metrics
- Interactive Plotly charts

### Sector Analysis
- Sector-wise performance
- Market-cap distribution
- Sector comparison

### Capital Allocation
- Capital allocation insights
- Treemap visualization
- Company comparison

### Annual Reports
- Company annual report repository
- Quick report access

---

## Analytics Outputs

The analytics module generates the following reports inside the `output/` directory:

- valuation_summary.xlsx
- valuation_flags.csv
- pe_trend.xlsx
- pb_vs_roe.xlsx
- ev_ebitda_comparison.xlsx
- dividend_yield_ranker.xlsx

---

## Dataset

The platform is built using financial data for 92 Nifty 100 companies, including:

- Company Information
- Financial Ratios
- Market Capitalization
- Profit & Loss
- Balance Sheet
- Cash Flow
- Sector Information

---

## Future Improvements

- Additional financial ratios
- Portfolio tracking
- Automated data refresh
- Enhanced dashboard visualizations
- Comprehensive automated testing