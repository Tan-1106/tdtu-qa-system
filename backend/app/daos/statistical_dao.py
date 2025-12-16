from bson import ObjectId
from datetime import datetime, timezone

from app.databases import mongo
from app.utils import serializer
from app.utils.api_response import DatabaseException


class StatisticalDao:
    def __init__(self):
        self.qa_collection = mongo.get_popular_questions_collection()
        
    # Store popular questions statistics record
    async def store_popular_questions(self, popular_questions: list):
        # Reset statistics collection
        await self.qa_collection.delete_many({})

        # Insert new popular questions records
        result = []
        for item in popular_questions:
            item["created_at"] = datetime.now(timezone.utc)
            await self.qa_collection.insert_one(item)
            result.append(serializer.popular_question_statistics_serialize(item))
        return result
    
    
    # Count popular questions records
    async def count_popular_questions(self, is_display: bool, faculty: str = None) -> int:
        query = {}
        if faculty:
            query["$or"] = [
                {"summary.faculty_scope": faculty},
            ]
        if is_display is not None:
            query["is_display"] = is_display 
            
        count = await self.qa_collection.count_documents(query)
        return count
    
    
    # Get popular questions statistics records
    async def get_popular_questions(self, skip: int, limit: int, is_display: bool = None, faculty: str = None) -> list:
        records = []
        query = {}
        if faculty:
            query["$or"] = [
                {"summary.faculty_scope": faculty},
            ]
        if is_display is not None:
            query["is_display"] = is_display 
            
        cursor = self.qa_collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        async for document in cursor:
            records.append(serializer.popular_question_statistics_serialize(document))
        return [record for record in records]
    
    
    # Update popular question status
    async def toggle_popular_question_display(self, question_id: str) -> dict:
        question = await self.qa_collection.find_one({"_id": ObjectId(question_id)})
        if not question:
            raise DatabaseException(f"Popular question with ID {question_id} not found")
        
        result = await self.qa_collection.update_one(
            {"_id": ObjectId(question_id)},
            {"$set": {"is_display": not question["is_display"], "updated_at": datetime.now(timezone.utc)}}
        )
        if result.matched_count == 0:
            raise DatabaseException(f"Popular question with ID {question_id} not found")
        
        updated_record = await self.qa_collection.find_one({"_id": ObjectId(question_id)})
        return serializer.popular_question_statistics_serialize(updated_record)
    
    
    # Assign faculty scope to popular question
    async def assign_faculty_scope_to_popular_question(self, question_id: str, faculty: str) -> dict:
        result = await self.qa_collection.update_one(
            {"_id": ObjectId(question_id)},
            {"$set": {"summary.faculty_scope": faculty, "updated_at": datetime.now(timezone.utc)}}
        )
        if result.matched_count == 0:
            raise DatabaseException(f"Popular question with ID {question_id} not found")
        
        updated_record = await self.qa_collection.find_one({"_id": ObjectId(question_id)})
        return serializer.popular_question_statistics_serialize(updated_record)
    
    
    # Update popular question
    async def update_popular_question(self, question_id: str, update_data: dict) -> dict:
        update_fields = {}
        if "question" in update_data:
            update_fields["question"] = update_data["question"]
        if "answer" in update_data:
            update_fields["answer"] = update_data["answer"]
        
        if not update_fields:
            raise DatabaseException("No valid fields to update.")
        
        update_fields["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.qa_collection.update_one(
            {"_id": ObjectId(question_id)},
            {"$set": update_fields}
        )
        if result.matched_count == 0:
            raise DatabaseException(f"Popular question with ID {question_id} not found")
        
        updated_record = await self.qa_collection.find_one({"_id": ObjectId(question_id)})
        return serializer.popular_question_statistics_serialize(updated_record)
    
    
    # Get popular question by ID
    async def get_popular_question_by_id(self, question_id: str) -> dict:
        document = await self.qa_collection.find_one({"_id": ObjectId(question_id)})
        if not document:
            raise DatabaseException(f"Popular question with ID {question_id} not found")
        return serializer.popular_question_statistics_serialize(document)