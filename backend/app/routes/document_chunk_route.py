from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, UploadFile, Form, Query

from app.services import auth_service
from app.utils.api_response import api_response
from app.controllers import document_chunk_controller

# --- ROUTER ---
router = APIRouter(
    prefix="/document-chunks",
    tags=["Document Chunks"],
    dependencies=[
        Depends(auth_service.require_role(["Admin"]))
    ]
)


# --- ROUTES ---
# Get document chunks by document ID with pagination
@router.get("/{doc_id}/")
async def get_document_chunks(
    doc_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    document_chunks = await document_chunk_controller.get_document_chunks(doc_id, page, limit)
    return api_response(
        status_code=200,
        message="Document chunks retrieved successfully.",
        details=document_chunks
    )