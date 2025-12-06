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
    
    
    # Get all document chunks
    async def get_all_document_chunks(self) -> list[dict]:
        cursor = self.document_chunks_collection.find({})
        document_chunks = []
        async for document_chunk in cursor:
            document_chunks.append(serializer.document_chunk_serialize(document_chunk))
        return document_chunks
    
    
    # Update chunk's embedding_id by document ID and chunk index
    async def update_chunk_embedding_id(
        self,
        doc_id: str,
        chunk_index: int,
        embedding_index: int, embedding_id: str
    ):
        field_path = f"chunks.{chunk_index}.embedding_ids.{embedding_index}"
        result = await self.document_chunks_collection.update_one(
            {"doc_id": doc_id},
            {"$set": {field_path: embedding_id}}
        )
        if result.matched_count == 0:
            raise DatabaseException(f"Document chunk with doc_id {doc_id} not found")
        return result.modified_count > 0
        
        
    # Delete document chunks by document ID
    async def delete_document_chunks_by_doc_id(self, doc_id: str):
        await self.document_chunks_collection.delete_many({"doc_id": doc_id})