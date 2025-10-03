from bson import ObjectId
from typing import List, Optional
from datetime import datetime, timezone

from app.utils.serializer import document_serialize
from app.database.mongo import get_documents_collection
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse

# CRUD Operations
# Read all documents
async def get_documents() -> List[DocumentResponse]:
    docs = []
    async for doc in get_documents_collection().find():
        docs.append(DocumentResponse(**document_serialize(doc)))
    return docs    

# Read a document by ID
async def get_document_by_id(doc_id: str) -> Optional[DocumentResponse]:
    if not ObjectId.is_valid(doc_id):
        return None
    doc = await get_documents_collection().find_one({"_id": ObjectId(doc_id)})
    if doc:
        return DocumentResponse(**document_serialize(doc))
    return None

# Create a new document
async def create_document(doc: DocumentCreate) -> DocumentResponse:
    doc["created_at"] = datetime.now(timezone.utc)
    result = await get_documents_collection().insert_one(doc)
    created_doc = await get_documents_collection().find_one({"_id": result.inserted_id})
    return DocumentResponse(**document_serialize(created_doc))

# Update an existing document
async def update_document(doc_id: str, doc_update: DocumentUpdate) -> Optional[DocumentResponse]:
    if not ObjectId.is_valid(doc_id):
        return None
    
    if doc_update:
        doc_update["updated_at"] = datetime.now(timezone.utc)
        result = await get_documents_collection().update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": doc_update}
        )
        if result.modified_count == 1:
            updated_doc = await get_documents_collection().find_one({"_id": ObjectId(doc_id)})
            if updated_doc:
                return DocumentResponse(**document_serialize(updated_doc))
    return None

# Delete a document by ID
async def delete_document(doc_id: str) -> bool:
    if not ObjectId.is_valid(doc_id):
        return False
    result = await get_documents_collection().delete_one({"_id": ObjectId(doc_id)})
    return result.deleted_count == 1