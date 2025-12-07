from datetime import datetime, timezone

from app.databases import mongo
from app.utils import serializer
from app.utils.api_response import DatabaseException

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
    
    
    # Update document chunks record
    async def update_document_chunks_record(self, doc_id: str, updated_chunks_record: dict):
        result = await self.document_chunks_collection.update_one(
            {"doc_id": doc_id},
            {"$set": {"chunks": updated_chunks_record, "updated_at": datetime.now(timezone.utc)}}
        )
        if result.matched_count == 0:
            raise DatabaseException(f"Document chunks record with doc_id {doc_id} not found")
        return result.modified_count > 0
    
    # Get all document chunks
    async def get_all_document_chunks(self) -> list[dict]:
        cursor = self.document_chunks_collection.find({})
        document_chunks = []
        async for document_chunk in cursor:
            document_chunks.append(serializer.document_chunk_serialize(document_chunk))
        return document_chunks
    
    
    # Count document chunks by document ID
    async def count_document_chunks(self, doc_id: str) -> int:
        chunks_record = await self.document_chunks_collection.find_one({"doc_id": doc_id})
        if not chunks_record:
            return 0
        chunks = chunks_record.get("chunks", {})
        return len(chunks)
    
    
    # Get document chunks by document ID
    async def get_document_chunks(self, doc_id: str, skip: int, limit: int) -> dict:
        chunks_record = await self.document_chunks_collection.find_one({"doc_id": doc_id})
        if not chunks_record:
            return {}
        
        chunks = chunks_record.get("chunks", {})
        chunks_list = sorted(chunks.items(), key=lambda x: int(x[0]))
        paginated_items = chunks_list[skip:skip + limit]
        
        paginated_chunks = {k: v for k, v in paginated_items}
        return paginated_chunks
    
    
    # Get document chunk by document ID and chunk index
    async def get_document_chunk_by_index(self, doc_id: str, chunk_index: int) -> dict:
        chunks_record = await self.document_chunks_collection.find_one({"doc_id": doc_id})
        if not chunks_record:
            raise DatabaseException(f"Document chunks record with doc_id {doc_id} not found")
        
        chunks = chunks_record.get("chunks", {})
        chunk_data = chunks.get(str(chunk_index))
        if not chunk_data:
            raise DatabaseException(f"Chunk index {chunk_index} not found in document chunks for doc_id {doc_id}")
        
        return chunk_data
    
    
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