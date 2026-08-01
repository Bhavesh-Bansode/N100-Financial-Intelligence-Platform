# 📈 Bluestock N100 Financial Intelligence Platform

> An end-to-end financial analytics platform for analysing Nifty 100 companies through automated ETL pipelines, financial KPI computation, advanced analytics, FastAPI REST APIs, and an interactive Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-REST-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

# Project Overview

The **Bluestock N100 Financial Intelligence Platform** is a comprehensive financial analytics and decision-support system designed to analyse companies listed in the **Nifty 100 Index**.

The platform automates the complete financial data lifecycle, including data ingestion, validation, KPI computation, financial analysis, clustering, valuation, portfolio analytics, peer comparison, and report generation.

It combines a robust ETL pipeline, relational database, analytical engine, REST API, and interactive dashboard into a single unified application.

The system enables analysts, investors, researchers, and students to perform detailed financial analysis without manually processing large financial datasets.

---

# Key Features

## Data Engineering

- Automated ETL Pipeline
- Data Cleaning & Normalisation
- Financial Data Validation
- SQLite Database Integration
- KPI Computation Engine

## Financial Analytics

- Company Financial Analysis
- Financial Ratio Analysis
- Growth Analysis
- Profitability Analysis
- Liquidity Analysis
- Leverage Analysis
- Valuation Metrics
- Sector Benchmarking
- Peer Comparison

## Advanced Analytics

- K-Means Company Clustering
- Cluster Profiling
- Correlation Analysis
- Portfolio Statistics
- Outlier Detection
- Trend Analysis

## Dashboard

- Interactive Streamlit Dashboard
- Company Profile
- Stock Screener
- Sector Analysis
- Portfolio Analytics
- Cluster Visualisation
- PDF Tearsheet Generation
- Interactive Plotly Charts

## API

- FastAPI REST Backend
- Company APIs
- Screener APIs
- Portfolio APIs
- Sector APIs
- Swagger Documentation

---

# Technology Stack

| Category | Technologies |
|-----------|--------------|
| Programming Language | Python |
| Database | SQLite |
| Backend | FastAPI |
| Frontend | Streamlit |
| Data Processing | Pandas, NumPy |
| Visualisation | Plotly, Matplotlib |
| Machine Learning | Scikit-Learn |
| ORM | SQLAlchemy |
| Testing | Pytest |
| Documentation | OpenAPI (Swagger) |

---

# Project Architecture

```
                Raw Financial Data
                       │
                       ▼
              ETL & Data Validation
                       │
                       ▼
                SQLite Database
                       │
          ┌────────────┴─────────────┐
          ▼                          ▼
     KPI Engine                Analytics Engine
          │                          │
          └────────────┬─────────────┘
                       ▼
                 FastAPI Backend
                       │
                       ▼
             Streamlit Dashboard
                       │
                       ▼
          Reports • Visualisations • PDFs
```

---

# Project Structure

```
Bluestock-N100-Financial-Intelligence-Platform/

├── data/
│   ├── raw/
│   ├── supporting/
│   └── nifty100.db
│
├── docs/
│   └── Professional_Analyst_Manual.docx
│
├── output/
│   ├── cluster_labels.csv
│   ├── cluster_profiles.csv
│   ├── portfolio_stats.csv
│   ├── outlier_report.csv
│   ├── valuation_summary.xlsx
│   └── ...
│
├── reports/
│   ├── elbow_plot.png
│   ├── correlation_heatmap.png
│   └── pytest_report.html
│
├── src/
│   ├── api/
│   ├── analytics/
│   ├── dashboard/
│   ├── etl/
│   ├── kpi/
│   └── utils/
│
├── tests/
├── requirements.txt
├── app.py
└── README.md
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/<username>/bluestock-n100-financial-intelligence-platform.git

cd bluestock-n100-financial-intelligence-platform
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Project

## Run ETL

```bash
python src/etl/loader.py
```

---

## Generate KPIs

```bash
python src/kpi/ratio_engine.py
```

---

## Start FastAPI

```bash
uvicorn src.api.main:app --reload --port 8000
```

Swagger Documentation

```
http://localhost:8000/docs
```

---

## Launch Dashboard

```bash
streamlit run app.py
```

---

# Dashboard Modules

## Home

- Platform Overview
- Summary Statistics
- Navigation

## Company Profile

- Financial Overview
- Key Ratios
- Growth Metrics
- Profitability
- Historical Trends

## Screener

Filter companies using

- ROE
- ROCE
- Debt/Equity
- Revenue CAGR
- Profit CAGR
- P/E
- Market Cap
- Sector
- Valuation Metrics

## Sector Analysis

- Sector Performance
- Industry Comparison
- Financial Benchmarks

## Peer Comparison

- Side-by-side comparison
- Financial metrics
- Growth comparison
- Ratio comparison

## Cluster Analysis

- KMeans clusters
- Cluster Profiles
- Company Segmentation

## Portfolio Statistics

- Mean
- Median
- Standard Deviation
- Distribution
- Portfolio Summary

## Documents

- Financial Reports
- PDF Tearsheets
- Generated Reports

---

# Generated Outputs

The platform automatically generates

```
output/

cluster_labels.csv
cluster_profiles.csv
portfolio_stats.csv
outlier_report.csv
valuation_summary.xlsx
valuation_flags.csv
```

```
reports/

correlation_heatmap.png
elbow_plot.png
pytest_report.html
```

---

# Testing

Run all tests

```bash
pytest tests -v
```

Generate HTML report

```bash
pytest --html=reports/pytest_report.html
```

Code Formatting

```bash
black src tests
```

Static Analysis

```bash
ruff check src tests
```

---

# Future Enhancements

- PostgreSQL Integration
- Docker Support
- Kubernetes Deployment
- Redis Caching
- Authentication & User Management
- Cloud Deployment (AWS/Azure/GCP)
- Real-Time Market Data
- Machine Learning-Based Stock Recommendation
- Portfolio Optimisation
- Automated Scheduled ETL Pipelines

---

# Documentation

Complete project documentation is available in:

```
docs/
Professional_Analyst_Manual.docx
```

---

# License

This project is released under the MIT License.

---

# Acknowledgements

Developed as part of the **Bluestock Fintech Internship Capstone Project**, demonstrating end-to-end financial data engineering, analytics, and dashboard development using modern Python technologies.
