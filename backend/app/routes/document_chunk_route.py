from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder

from app.services import auth_service
from app.schemas import document_schema
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
@router.get("/{doc_id}")
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
    
    
# Add a potential questions for a specific chunk
@router.post("/{doc_id}/chunks/{chunk_index}/potential-questions")
async def add_potential_question(
    doc_id: str,
    chunk_index: int,
    question_data: document_schema.UpdateChunkQuestionSchema
):
    question_data = jsonable_encoder(question_data)
    updated_chunk = await document_chunk_controller.add_potential_question(doc_id, chunk_index, question_data["question"])
    return api_response(
        status_code=200,
        message="Potential question added successfully.",
        details=updated_chunk
    )
    
    
# Delete a potential question for a specific chunk
@router.delete("/{doc_id}/chunks/{chunk_index}/potential-questions/{question_index}")
async def delete_potential_question(
    doc_id: str,
    chunk_index: int,
    question_index: int
):
    await document_chunk_controller.delete_potential_question(doc_id, chunk_index, question_index)
    return api_response(
        status_code=200,
        message="Potential question deleted successfully.",
        details=None
    )