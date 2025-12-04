from bson import ObjectId
from datetime import datetime, timezone

from app.databases import mongo
from app.utils import serializer
from app.utils.api_response import DatabaseException
from app.utils.basic_information import Role, Faculty

class DocumentChunkDAO:
    def __init__(self):
        self.document_chunks_collection = mongo.get_document_chunks_collection()
        
        
    # Create a new document chunks record
    async def create_document_chunks_record(self, document_chunks_record: dict) -> dict:
        document_chunks_record["created_at"] = datetime.now(timezone.utc)
        result = await self.document_chunks_collection.insert_one(document_chunks_record)
        created_record = await self.document_chunks_collection.find_one({"_id": result.inserted_id})
        if not created_record:
            raise DatabaseException("Failed to create document chunks record")
        
        return serializer.document_chunk_serialize(created_record)
        
        
    # Delete document chunks by document ID
    async def delete_document_chunks_by_doc_id(self, doc_id: str):
        await self.document_chunks_collection.delete_many({"doc_id": doc_id})