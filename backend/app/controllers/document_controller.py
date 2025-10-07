from app.schemas import document_schema
from app.services import document_service
from fastapi.encoders import jsonable_encoder

# Get all documents
async def get_documents():
    response = await document_service.get_documents()
    return response

# Get a document by ID
async def get_document_by_id(doc_id: str):
    response = await document_service.get_document_by_id(doc_id)
    return response

# Create a new document
async def create_document(doc_data: document_schema.DocumentCreate):
    doc_data = jsonable_encoder(doc_data)
    response = await document_service.create_document(doc_data)
    return response

# Update an existing document
async def update_document(doc_id: str, doc_update: document_schema.DocumentUpdate):
    update_data = jsonable_encoder(doc_update)
    if len(doc_update) == 1 and "edited_by" in doc_update:
            raise ValueError("No fields to update.")
    response = await document_service.update_document(doc_id, update_data)
    return response

# Delete a document by ID
async def delete_document(doc_id: str) -> bool:
    response = await document_service.delete_document(doc_id)
    return response