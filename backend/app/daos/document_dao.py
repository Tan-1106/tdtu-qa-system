from bson import ObjectId
from datetime import datetime, timezone

from app.databases import mongo
from app.utils import serializer
from app.utils.api_response import DatabaseException

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
    
    
    # Count general documents with filters
    async def count_general_documents(self, doc_type: str, department: str, keyword: str) -> int:
        query = {"faculty": None}
        if doc_type:
            query["doc_type"] = doc_type
        if department:
            query["department"] = department
        if keyword:
            query["$or"] = [
                {"file_name": {"$regex": keyword, "$options": "i"}}
            ]
            
        total = await self.documents_collection.count_documents(query)
        return total 
    
    
    # Get general documents with filters and pagination
    async def get_general_documents(self, skip: int, limit: int, doc_type: str, department: str, keyword: str) -> list[dict]:
        query = {"faculty": None}
        if doc_type:
            query["doc_type"] = doc_type
        if department:
            query["department"] = department
        if keyword:
            query["$or"] = [
                {"file_name": {"$regex": keyword, "$options": "i"}}
            ]
            
        cursor = self.documents_collection.find(query).skip(skip).limit(limit).sort("uploaded_at", -1)
        documents = []
        async for document in cursor:
            documents.append(serializer.document_serialize(document))
        return documents
    
    
    # Count faculty documents with filters
    async def count_faculty_documents(self, faculty: str, doc_type: str, keyword: str) -> int:
        query = {}
        if faculty:
            query["faculty"] = faculty
        else:
            query["department"] = None
        if doc_type:
            query["doc_type"] = doc_type
        if keyword:
            query["$or"] = [
                {"file_name": {"$regex": keyword, "$options": "i"}}
            ]
            
        total = await self.documents_collection.count_documents(query)
        return total
    
    
    # Get faculty documents with filters and pagination
    async def get_faculty_documents(self, faculty: str, skip: int, limit: int, doc_type: str, keyword: str) -> list[dict]:
        query = {}
        if faculty:
            query["faculty"] = faculty
        else:
            query["department"] = None
        if doc_type:
            query["doc_type"] = doc_type
        if keyword:
            query["$or"] = [
                {"file_name": {"$regex": keyword, "$options": "i"}}
            ]
            
        cursor = self.documents_collection.find(query).skip(skip).limit(limit).sort("uploaded_at", -1)
        documents = []
        async for document in cursor:
            documents.append(serializer.document_serialize(document))
        return documents
    
    
    # Get all existing departments
    async def get_all_existing_departments(self) -> list[str]:
        departments = await self.documents_collection.distinct("department", {"department": {"$ne": None}})
        return departments
    
    
    # Get all existing document types
    async def get_all_existing_doc_types(self) -> list[str]:
        doc_types = await self.documents_collection.distinct("doc_type", {"doc_type": {"$ne": None}})
        return doc_types
    
    
    # Get a document by ID
    async def get_document_by_id(self, doc_id: str) -> dict:
        document = await self.documents_collection.find_one({"_id": ObjectId(doc_id)})
        if not document:
            raise DatabaseException("Document not found.")
        return serializer.document_serialize(document)
    
    
    # Get document file info by ID
    async def get_document_file_info(self, doc_id: str) -> tuple[str, str]:
        document = await self.documents_collection.find_one({"_id": ObjectId(doc_id)})
        if not document:
            raise DatabaseException("Document not found.")
        file_name = document.get("file_name", "")
        file_url = document.get("file_url", "")
        return file_name, file_url
    
    
    # Update a document by ID
    async def update_document(self, doc_id: str, data: dict) -> dict:
        data["updated_at"] = datetime.now(timezone.utc)
        result = await self.documents_collection.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": data}
        )
        if result.matched_count == 0:
            raise DatabaseException("Document not found.")
        
        updated_document = await self.documents_collection.find_one({"_id": ObjectId(doc_id)})
        return serializer.document_serialize(updated_document)
    
    
    # Delete a document by ID
    async def delete_document(self, doc_id: str):
        result = await self.documents_collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0