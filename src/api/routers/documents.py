"""Document endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/")
def get_documents_status():
    return {"status": "ok"}
