from app.databases import mongo

from app.utils.api_response import DatabaseException

class QADao:
    def __init__(self):
        self.qa_collection = mongo.get_qa_collection()
        
    # Create a new QA record
    async def create_qa_record(self, qa_record: dict) -> dict:
        result = await self.qa_collection.insert_one(qa_record)
        created_record = await self.qa_collection.find_one({"_id": result.inserted_id})
        if not created_record:
            raise DatabaseException("Failed to create QA record")
        
        return created_record
        