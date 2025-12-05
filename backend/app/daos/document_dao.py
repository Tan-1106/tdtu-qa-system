from bson import ObjectId
from datetime import datetime, timezone

from app.databases import mongo
from app.utils import serializer
from app.utils.api_response import DatabaseException
from app.utils.basic_information import Role, Faculty

class DocumentDAO:
    def __init__(self):
        self.documents_collection = mongo.get_documents_collection()


    # Create a new document
    async def create_document(self, document: dict) -> dict:
        document["uploaded_at"] = datetime.now(timezone.utc)
        result = await self.documents_collection.insert_one(document)
        created_document = await self.documents_collection.find_one({"_id": result.inserted_id})
        if not created_document:
            raise Exception("Failed to create document record.")
        
        return serializer.document_serialize(created_document)
    
    
    # Count all documents
    async def count_all_documents(self, doc_type: str = None, department: str = None, faculty: str = None, keyword: str = None) -> int:
        query = {}
        if doc_type:
            query["doc_type"] = doc_type
        if department:
            query["department"] = department
        if faculty:
            query["faculty"] = faculty
        if keyword:
            query["$or"] = [
            {"file_name": {"$regex": keyword, "$options": "i"}}
        ]
            
        count = await self.documents_collection.count_documents(query)
        return count
    
    
    # Get documents with pagination and filters
    async def get_documents(self, skip: int, limit: int, doc_type: str = None, department: str = None, faculty: str = None, keyword: str = None) -> list[dict]:
        documents = []
        query = {}
        if doc_type:
            query["doc_type"] = doc_type
        if department:
            query["department"] = department
        if faculty:
            query["faculty"] = faculty
        if keyword:
            query["$or"] = [
            {"file_name": {"$regex": keyword, "$options": "i"}}
        ]
            
        cursor = self.documents_collection.find(query).skip(skip).limit(limit)
        async for document in cursor:
            documents.append(serializer.document_serialize(document))
        return documents
    
    
    # Delete a document by ID
    async def delete_document(self, doc_id: str):
        result = await self.documents_collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0