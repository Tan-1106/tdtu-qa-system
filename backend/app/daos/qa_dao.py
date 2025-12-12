from bson import ObjectId
from datetime import datetime, timedelta, timezone

from app.databases import mongo
from app.utils import serializer
from app.schemas import qa_schema
from app.utils.api_response import DatabaseException
from app.schemas.statistical_schema import PeriodType


class QADao:
    def __init__(self):
        self.qa_collection = mongo.get_qa_collection()
        
    # Create a new QA record
    async def create_qa_record(self, qa_record: dict) -> dict:
        qa_record["created_at"] = datetime.now(timezone.utc)
        result = await self.qa_collection.insert_one(qa_record)
        created_record = await self.qa_collection.find_one({"_id": result.inserted_id})
        if not created_record:
            raise DatabaseException("Failed to create QA record")
        return qa_schema.QARecordSchema(**serializer.qa_session_serialize(created_record))
    
    
    # Update QA record by ID
    async def update_qa_answer(self, qa_id: str, answer: str) -> dict:
        result = await self.qa_collection.update_one(
            {"_id": ObjectId(qa_id)},
            {"$set": {"answer": answer, "updated_at": datetime.now(timezone.utc)}}
        )
        if result.matched_count == 0:
            raise DatabaseException(f"QA record with qa_id {qa_id} not found")
        
        updated_record = await self.qa_collection.find_one({"_id": ObjectId(qa_id)})
        return qa_schema.QARecordSchema(**serializer.qa_session_serialize(updated_record))
    
    
    # Count all QA records
    async def count_all_qa_records(self, feedback: str, faculty: str, keyword: str, has_manager_answer: bool) -> int:
        query = {}
        if feedback:
            query["feedback"] = feedback
        if faculty:
            query["user_faculty"] = faculty
        if keyword:
            query["$or"] = [
                {"question": {"$regex": keyword, "$options": "i"}},
                {"user_sub": {"$regex": keyword, "$options": "i"}}
            ]
        if has_manager_answer is not None:
            if has_manager_answer:
                query["manager_answer"] = {"$exists": True, "$nin": [None, ""]}
            else:
                query["$or"] = [
                    {"manager_answer": {"$exists": False}},
                    {"manager_answer": None},
                    {"manager_answer": ""}
                ]
        count = await self.qa_collection.count_documents(query)
        return count
    
    
    # Get all QA records
    async def get_all_question_records(self, skip: int, limit: int, feedback: str, faculty: str, keyword: str, has_manager_answer: bool) -> list[dict]:
        query = {}
        if feedback:
            query["feedback"] = feedback
        if faculty:
            query["user_faculty"] = faculty
        if keyword:
            query["$or"] = [
                {"question": {"$regex": keyword, "$options": "i"}},
                {"user_sub": {"$regex": keyword, "$options": "i"}}
            ]
        if has_manager_answer is not None:
            if has_manager_answer:
                query["manager_answer"] = {"$exists": True, "$nin": [None, ""]}
            else:
                query["$or"] = [
                    {"manager_answer": {"$exists": False}},
                    {"manager_answer": None},
                    {"manager_answer": ""}
                ]
        cursor = self.qa_collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        records = []
        async for record in cursor:
            records.append(qa_schema.QARecordSchema(**serializer.qa_session_serialize(record)))
        return records
    
    
    # Count QA records by user ID
    async def count_qa_records_by_user_id(self, user_id: str, feedback: str, has_manager_answer: bool) -> int:
        query = {"user_id": user_id}
        if feedback:
            query["feedback"] = feedback
        if has_manager_answer is not None:
            if has_manager_answer:
                query["manager_answer"] = {"$exists": True, "$nin": [None, ""]}
            else:
                query["$or"] = [
                    {"manager_answer": {"$exists": False}},
                    {"manager_answer": None},
                    {"manager_answer": ""}
                ]
        count = await self.qa_collection.count_documents(query)
        return count
    
    
    # Get QA records by user ID
    async def get_question_records_by_user_id(self, user_id: str, skip: int, limit: int, feedback: str, has_manager_answer: bool) -> list[dict]:
        query = {"user_id": user_id}
        if feedback:
            query["feedback"] = feedback
        if has_manager_answer is not None:
            if has_manager_answer:
                query["manager_answer"] = {"$exists": True, "$nin": [None, ""]}
            else:
                query["$or"] = [
                    {"manager_answer": {"$exists": False}},
                    {"manager_answer": None},
                    {"manager_answer": ""}
                ]
        cursor = self.qa_collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        records = []
        async for record in cursor:
            records.append(qa_schema.QARecordSchema(**serializer.qa_session_serialize(record)))
        return records
        
        
    # Get QA record by ID
    async def get_qa_record_by_id(self, qa_id: str) -> dict:
        qa_record = await self.qa_collection.find_one({"_id": ObjectId(qa_id)})
        if not qa_record:
            raise DatabaseException(f"QA record with qa_id {qa_id} not found")
        return qa_schema.QARecordSchema(**serializer.qa_session_serialize(qa_record))
    
    
    # Leave feedback for a question
    async def leave_feedback_for_question(self, qa_record_id: str, feedback: str, user_id: str) -> bool:
        result = await self.qa_collection.update_one(
            {"_id": ObjectId(qa_record_id), "user_id": user_id},
            {"$set": {"feedback": feedback, "updated_at": datetime.now(timezone.utc)}}
        )
        if result.matched_count == 0:
            raise DatabaseException(f"QA record with qa_record_id {qa_record_id} not found or user unauthorized")
        return result.modified_count == 1
    
    
    # Reply to a question
    async def reply_to_question(self, qa_record_id: str, manager_answer: str) -> dict:
        result = await self.qa_collection.update_one(
            {"_id": ObjectId(qa_record_id)},
            {"$set": {"manager_answer": manager_answer, "updated_at": datetime.now(timezone.utc)}}
        )
        if result.matched_count == 0:
            raise DatabaseException(f"QA record with qa_record_id {qa_record_id} not found")
        updated_record = await self.get_qa_record_by_id(qa_record_id)
        return updated_record
    
    
    # Get all QA records by period type
    async def get_qa_records_by_period_type(self, period_type: PeriodType) -> list[dict]:
        now = datetime.now(timezone.utc)
        
        if period_type == PeriodType.Weekly:
            start_date = now - timedelta(weeks=1)
        elif period_type == PeriodType.Monthly:
            start_date = now - timedelta(days=30)
        elif period_type == PeriodType.Yearly:
            start_date = now - timedelta(days=365)
        else:
            raise ValueError("Invalid period type")
        
        query = {"created_at": {"$gte": start_date, "$lte": now}}
        cursor = self.qa_collection.find(query)
        
        records = []
        async for record in cursor:
            records.append(qa_schema.QARecordSchema(**serializer.qa_session_serialize(record)))
        return start_date, now, records
    
    
    # Count total questions
    async def questions_statistics(self, period_type: PeriodType) -> dict:
        now = datetime.now(timezone.utc)
        
        if period_type == PeriodType.Weekly:
            start_date = now - timedelta(weeks=1)
        elif period_type == PeriodType.Monthly:
            start_date = now - timedelta(days=30)
        elif period_type == PeriodType.Yearly:
            start_date = now - timedelta(days=365)
        else:
            raise ValueError("Invalid period type")
        
        query = {"created_at": {"$gte": start_date, "$lte": now}}
        
        # Count total questions
        total = await self.qa_collection.count_documents(query)
        
        # Count questions with Like feedback
        like_query = {**query, "feedback": "Like"}
        like_count = await self.qa_collection.count_documents(like_query)
        
        # Count questions with Dislike feedback
        dislike_query = {**query, "feedback": "Dislike"}
        dislike_count = await self.qa_collection.count_documents(dislike_query)
        
        return {
            "total": total,
            "like": like_count,
            "dislike": dislike_count
        }
        
        