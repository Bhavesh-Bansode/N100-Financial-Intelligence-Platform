"""Service health endpoint."""

from time import perf_counter

from fastapi import APIRouter, Request

from src.api.main import API_VERSION, get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def get_health(request: Request):
    """Return service status, uptime, version and all SQLite table row counts."""
    with get_db() as connection:
        table_names = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        row_counts = {
            row["name"]: connection.execute(
                f'SELECT COUNT(*) FROM "{row["name"]}"'
            ).fetchone()[0]
            for row in table_names
        }

    started_at = getattr(request.app.state, "started_at", perf_counter())
    return {
        "status": "ok",
        "db_row_counts": row_counts,
        "uptime_seconds": round(perf_counter() - started_at, 3),
        "version": API_VERSION,
    }
