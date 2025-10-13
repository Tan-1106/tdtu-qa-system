from bson import ObjectId
from typing import List, Optional
from datetime import datetime, timezone
from app.databases import mongo
from app.utils import serializer
from app.schemas import document_schema

# Read all documents
async def get_documents() -> List[document_schema.DocumentResponse]:
    docs = []
    async for doc in mongo.get_documents_collection().find():
        docs.append(document_schema.DocumentResponse(**serializer.document_serialize(doc)))
    return docs

# Read a document by ID
async def get_document_by_id(doc_id: str) -> Optional[document_schema.DocumentResponse]:
    doc = await mongo.get_documents_collection().find_one({"_id": ObjectId(doc_id)})
    if doc:
        return document_schema.DocumentResponse(**serializer.document_serialize(doc))
    return None

# Create a new document
async def create_document(doc: dict) -> document_schema.DocumentResponse:
    doc["created_at"] = datetime.now(timezone.utc)
    result = await mongo.get_documents_collection().insert_one(doc)
    created_doc = await mongo.get_documents_collection().find_one({"_id": result.inserted_id})
    return document_schema.DocumentResponse(**serializer.document_serialize(created_doc))

# Update an existing document
async def update_document(doc_id: str, doc_update: dict) -> Optional[document_schema.DocumentResponse]:
    if not ObjectId.is_valid(doc_id):
        return None
    if doc_update:
        doc_update["updated_at"] = datetime.now(timezone.utc)
        result = await mongo.get_documents_collection().update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": doc_update}
        )
        if result.modified_count == 1:
            updated_doc = await mongo.get_documents_collection().find_one({"_id": ObjectId(doc_id)})
            if updated_doc:
                return document_schema.DocumentResponse(**serializer.document_serialize(updated_doc))
    return None

# Delete a document by ID
async def delete_document(doc_id: str) -> bool:
    if not ObjectId.is_valid(doc_id):
        return False
    result = await mongo.get_documents_collection().delete_one({"_id": ObjectId(doc_id)})
    return result.deleted_count == 1