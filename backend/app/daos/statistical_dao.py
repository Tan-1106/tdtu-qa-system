from bson import ObjectId
from datetime import datetime, timezone

from app.databases import mongo
from app.utils import serializer
from app.schemas import statistical_schema
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
    
    
    # Get popular questions statistics records
    async def get_popular_questions(self) -> list:
        records = []
        cursor = self.qa_collection.find().sort("count", -1)
        async for document in cursor:
            records.append(serializer.popular_question_statistics_serialize(document))
        return records