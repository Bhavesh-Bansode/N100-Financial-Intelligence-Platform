"""FastAPI application for the Nifty 100 Financial Intelligence Platform."""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
import sqlite3
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "nifty100.db"
API_VERSION = "1.0.0"
logger = logging.getLogger("nifty100.api")


def get_db() -> sqlite3.Connection:
    """Open a SQLite connection for a single request or repository operation."""
    connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Record application start time used by the health endpoint."""
    app.state.started_at = perf_counter()
    yield


app = FastAPI(
    title="Nifty 100 Financial Intelligence API",
    version=API_VERSION,
    description="API for Nifty 100 company, portfolio, valuation and sector analytics.",
    lifespan=lifespan,
)

# Internal application: allow browser clients hosted on any origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request's method, path and completed response time."""
    started_at = perf_counter()
    try:
        return await call_next(request)
    finally:
        elapsed_ms = (perf_counter() - started_at) * 1000
        logger.info("%s %s completed in %.2f ms", request.method, request.url.path, elapsed_ms)


# Import routers after the shared database helpers have been defined. The health
# module imports those helpers, so this ordering avoids a circular import.
from src.api.routers import (  # noqa: E402
    companies,
    documents,
    health,
    market_cap,
    peers,
    portfolio,
    screener,
    sectors,
    valuation,
)


API_PREFIX = "/api/v1"
for router in (
    health.router,
    companies.router,
    screener.router,
    sectors.router,
    peers.router,
    valuation.router,
    portfolio.router,
    documents.router,
    market_cap.router,
): 
    app.include_router(router, prefix=API_PREFIX)
