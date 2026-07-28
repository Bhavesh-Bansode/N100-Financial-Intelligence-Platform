"""Database-backed company endpoints."""

from pathlib import Path
import re
import sqlite3
from typing import Any
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from src.api.main import get_db
from src.api.routers._data import LATEST_RATIOS_CTE, rows as data_rows


router = APIRouter(prefix="/companies", tags=["companies"])
PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEARSHEETS_DIR = PROJECT_ROOT / "reports" / "tearsheets"
YEAR_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def _rows(connection: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> list[dict]:
    return [dict(row) for row in connection.execute(query, params).fetchall()]


def _company_or_404(connection: sqlite3.Connection, ticker: str) -> dict:
    company = connection.execute(
        """
        SELECT c.*, s.broad_sector, s.sub_sector, s.index_weight_pct,
               s.market_cap_category
        FROM companies c
        LEFT JOIN sectors s ON s.company_id = c.id
        WHERE UPPER(c.id) = UPPER(?)
        """,
        (ticker,),
    ).fetchone()
    if company is None:
        raise HTTPException(status_code=404, detail=f"Company ticker '{ticker}' not found")
    return dict(company)


def _validate_year(value: str | None, parameter: str) -> str | None:
    if value is not None and not YEAR_PATTERN.fullmatch(value):
        raise HTTPException(status_code=422, detail=f"{parameter} must use YYYY-MM format")
    return value


def _history(
    table: str, ticker: str, from_year: str | None, to_year: str | None,
) -> list[dict]:
    from_year = _validate_year(from_year, "from_year")
    to_year = _validate_year(to_year, "to_year")
    if from_year and to_year and from_year > to_year:
        raise HTTPException(status_code=422, detail="from_year must not be later than to_year")

    clauses = ["company_id = ?"]
    params: list[str] = [ticker.upper()]
    if from_year:
        clauses.append("year >= ?")
        params.append(from_year)
    if to_year:
        clauses.append("year <= ?")
        params.append(to_year)

    with get_db() as connection:
        _company_or_404(connection, ticker)
        return _rows(
            connection,
            f"SELECT * FROM {table} WHERE {' AND '.join(clauses)} ORDER BY year",
            tuple(params),
        )


@router.get("")
def get_companies(
    sector: str | None = None,
    market_cap_category: str | None = None,
    search: str | None = None,
):
    """List companies, optionally filtered by sector, cap category or name/ticker."""
    clauses: list[str] = []
    params: list[str] = []
    if sector:
        clauses.append("LOWER(s.broad_sector) = LOWER(?)")
        params.append(sector)
    if market_cap_category:
        clauses.append("LOWER(s.market_cap_category) = LOWER(?)")
        params.append(market_cap_category)
    if search:
        clauses.append("(LOWER(c.company_name) LIKE LOWER(?) OR LOWER(c.id) LIKE LOWER(?))")
        search_term = f"%{search}%"
        params.extend([search_term, search_term])

    query = """
        SELECT c.id, c.company_name, s.broad_sector, s.sub_sector,
               c.roe_percentage AS roe_pct, c.roce_percentage AS roce_pct
        FROM companies c
        LEFT JOIN sectors s ON s.company_id = c.id
    """
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY c.company_name"

    with get_db() as connection:
        return _rows(connection, query, tuple(params))


@router.get("/{ticker}")
def get_company(ticker: str):
    """Return company and sector fields plus the latest complete annual KPI row."""
    with get_db() as connection:
        company = _company_or_404(connection, ticker)
        latest_kpis = connection.execute(
            """
            SELECT * FROM financial_ratios
            WHERE company_id = ?
              AND UPPER(year) != 'TTM'
            ORDER BY year DESC
            LIMIT 1
            """,
            (company["id"],),
        ).fetchone()
    company["latest_kpis"] = dict(latest_kpis) if latest_kpis else None
    return company


@router.get("/{ticker}/pl")
def get_profit_and_loss(
    ticker: str, from_year: str | None = Query(default=None), to_year: str | None = Query(default=None),
):
    """Return profit-and-loss history for a company."""
    return {"ticker": ticker.upper(), "history": _history("profitandloss", ticker, from_year, to_year)}


@router.get("/{ticker}/bs")
def get_balance_sheet(
    ticker: str, from_year: str | None = Query(default=None), to_year: str | None = Query(default=None),
):
    """Return balance-sheet history for a company."""
    return {"ticker": ticker.upper(), "history": _history("balancesheet", ticker, from_year, to_year)}


@router.get("/{ticker}/cashflow")
def get_cashflow(
    ticker: str, from_year: str | None = Query(default=None), to_year: str | None = Query(default=None),
):
    """Return cash-flow history for a company."""
    return {"ticker": ticker.upper(), "history": _history("cashflow", ticker, from_year, to_year)}


@router.get("/{ticker}/ratios")
def get_ratios(ticker: str, year: str | None = Query(default=None)):
    """Return all calculated ratio/KPI rows, optionally for one reporting year."""
    if year is not None and year.upper() != "TTM":
        _validate_year(year, "year")
    with get_db() as connection:
        company = _company_or_404(connection, ticker)
        query = "SELECT * FROM financial_ratios WHERE company_id = ?"
        params: tuple[str, ...] = (company["id"],)
        if year:
            query += " AND year = ?"
            params += (year,)
        query += " ORDER BY year"
        ratios = _rows(connection, query, params)
    return {"ticker": company["id"], "ratios": ratios}


@router.get("/{ticker}/tearsheet", response_class=FileResponse)
def download_tearsheet(ticker: str):
    """Download the pre-generated company tearsheet PDF."""
    with get_db() as connection:
        company = _company_or_404(connection, ticker)
    safe_name = "".join(character if character.isalnum() else "_" for character in company["company_name"])
    pdf_path = TEARSHEETS_DIR / f"{safe_name}_tearsheet.pdf"
    if not pdf_path.is_file():
        raise HTTPException(status_code=404, detail="Pre-generated tearsheet not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_path.name)


@router.get("/{ticker}/peers/compare")
def compare_with_peers(ticker: str):
    """Return eight radar axes for a company, its peer average and benchmark."""
    axes = [
        "return_on_equity_pct", "operating_profit_margin_pct", "net_profit_margin_pct",
        "revenue_cagr_5yr", "pat_cagr_5yr", "eps_cagr_5yr", "debt_to_equity",
        "interest_coverage",
    ]
    with get_db() as connection:
        company = _company_or_404(connection, ticker)
        group = connection.execute("""
            SELECT peer_group_name FROM peer_groups WHERE company_id = ? ORDER BY id LIMIT 1
        """, (company["id"],)).fetchone()
        if group is None:
            raise HTTPException(status_code=404, detail="Company does not belong to a peer group")
        members = data_rows(connection, LATEST_RATIOS_CTE + """
            SELECT pg.company_id, pg.is_benchmark, """ + ", ".join(f"lr.{axis}" for axis in axes) + """
            FROM peer_groups pg JOIN latest_ratios lr ON lr.company_id = pg.company_id
            WHERE pg.peer_group_name = ?
        """, (group["peer_group_name"],))
    target = next(member for member in members if member["company_id"] == company["id"])
    benchmark = next((member for member in members if str(member["is_benchmark"]).lower() in {"1", "true", "yes"}), None)
    radar_axes = []
    for axis in axes:
        values = [member[axis] for member in members if member[axis] is not None]
        radar_axes.append({
            "metric": axis,
            "company_value": target[axis],
            "peer_group_average": sum(values) / len(values) if values else None,
            "benchmark_value": benchmark[axis] if benchmark else None,
        })
    return {
        "ticker": company["id"], "peer_group": group["peer_group_name"],
        "benchmark_ticker": benchmark["company_id"] if benchmark else None, "axes": radar_axes,
    }


@router.get("/{ticker}/documents")
def get_documents(ticker: str):
    """Return annual-report links along with a structural URL-validity flag."""
    with get_db() as connection:
        company = _company_or_404(connection, ticker)
        documents = _rows(connection, """
            SELECT Year AS year, Annual_Report AS annual_report FROM documents
            WHERE company_id = ? ORDER BY Year DESC
        """, (company["id"],))
    for document in documents:
        parsed = urlparse(document["annual_report"] or "")
        document["is_url_valid"] = parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    return {"ticker": company["id"], "documents": documents}
