"""Valuation endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/valuation", tags=["valuation"])


@router.get("/")
def get_valuation_status():
    return {"status": "ok"}
