from typing import List
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from app.utils.api_response import success_response, error_response

from app.database.crud import documents
from app.schemas.document import DocumentCreate, DocumentUpdate

router = APIRouter(prefix="/documents", tags=["Documents"])

# Just for testing, logic is not implemented yet
# Get all documents
@router.get("/")
async def get_documents():
    try:
        docs = await documents.get_documents()
        return success_response(
            data=docs,
            message="Documents retrieved successfully.",
            status_code=200
        )
    except Exception as e:
        return error_response(message=str(e))
     
# Get a document by ID
@router.get("/{doc_id}")
async def get_document(doc_id: str):
    try:
        document = await documents.get_document_by_id(doc_id)
        if document:
            return success_response(
                data=document,
                message="Document retrieved successfully.",
                status_code=200
            )
        else:
            return error_response(message="Document not found.", status_code=404)
    except Exception as e:
        return error_response(message=str(e))

# Create a new document
@router.post("/")
async def create_document(doc: DocumentCreate):
    try:
        doc = jsonable_encoder(doc)
        created_doc = await documents.create_document(doc)
        return success_response(
            data=created_doc,
            message="Document created successfully.",
            status_code=201
        )
    except Exception as e:
        return error_response(message=str(e))
    
# Update a document by ID
@router.patch("/{doc_id}")
async def update_document(doc_id: str, doc_update: DocumentUpdate):
    try:
        doc_update = jsonable_encoder(doc_update)
        updated_doc = await documents.update_document(doc_id, doc_update)
        if updated_doc:
            return success_response(
                data=updated_doc,
                message="Document updated successfully.",
                status_code=200
            )
        else:
            return error_response(message="Document not found.", status_code=404)
    except Exception as e:
        return error_response(message=str(e))
    
# Delete a document by ID
@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    try:
        deleted = await documents.delete_document(doc_id)
        if deleted:
            return success_response(
                data=None,
                message="Document deleted successfully.",
                status_code=200
            )
        else:
            return error_response(message="Document not found.", status_code=404)
    except Exception as e:
        return error_response(message=str(e))