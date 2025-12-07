from bson import ObjectId
from datetime import datetime, timezone

from app.databases import mongo
from app.schemas import api_key_schema
from app.utils.serializer import api_key_serialize
from app.utils.api_response import DatabaseException

class APIKeyDAO:
    def __init__(self):
        self.api_keys_collection = mongo.get_api_keys_collection()


    # Create a new API key record
    async def create_api_key(self, api_key_data) -> dict:
        api_key_data["created_at"] = datetime.now(timezone.utc)
        api_key_data["is_using"] = False
        api_key_data["using_model"] = None
        
        result = await self.api_keys_collection.insert_one(api_key_data)
        created_key = await self.api_keys_collection.find_one({"_id": result.inserted_id})
        if not created_key:
            raise DatabaseException("Unable to create API key record.")
        return api_key_schema.APIKeyRecord(**api_key_serialize(created_key))


    # Count all API keys
    async def count_all_api_keys(self, keyword: str = None, provider: str = None) -> int:
        query = {}
        search_conditions = []
        
        if keyword:
            search_conditions.append({"name": {"$regex": keyword, "$options": "i"}})
            search_conditions.append({"description": {"$regex": keyword, "$options": "i"}})
            
        if provider:
            query["provider"] = provider
            
        if search_conditions:
            query["$or"] = search_conditions
            
        count = await self.api_keys_collection.count_documents(query)
        return count
    
    # Get all API keys
    async def get_all_api_keys(self) -> list[api_key_schema.APIKeyRecord]:
        api_keys = []
        cursor = self.api_keys_collection.find()
        async for key in cursor:
            api_keys.append(api_key_schema.APIKeyRecord(**api_key_serialize(key)))
        return api_keys
    
    
    # Get all API keys (Pagination)
    async def get_api_keys(self, skip: int, limit: int, keyword: str = None, provider: str = None) -> list[api_key_schema.APIKeyRecord]:
        api_keys = []
        query = {}
        search_conditions = []
        if keyword:
            search_conditions.append({"name": {"$regex": keyword, "$options": "i"}})
            search_conditions.append({"description": {"$regex": keyword, "$options": "i"}})
        if provider:
            query["provider"] = provider
        if search_conditions:
            query["$or"] = search_conditions
        cursor = self.api_keys_collection.find(query).skip(skip).limit(limit)
        async for key in cursor:
            api_keys.append(api_key_schema.APIKeyRecord(**api_key_serialize(key)))
        return api_keys
        
    # Get a single API key by ID
    async def get_api_key_by_id(self, key_id: str) -> dict | None:
        api_key = await self.api_keys_collection.find_one({"_id": ObjectId(key_id)})
        if api_key:
            return api_key_schema.APIKeyRecord(**api_key_serialize(api_key))
        return None
    
    
    # Get current using API key
    async def get_current_using_api_key(self) -> dict | None:
        api_key = await self.api_keys_collection.find_one({"is_using": True})
        if api_key:
            return api_key_schema.APIKeyRecord(**api_key_serialize(api_key))
        return None
    

    # Update an existing API key record
    async def update_api_key(self, key_id: str, update_data: dict) -> dict:
        update_data["updated_at"] = datetime.now(timezone.utc)
        result = await self.api_keys_collection.update_one(
            {"_id": ObjectId(key_id)},
            {"$set": update_data}
        )
        if result.modified_count != 1:
            raise DatabaseException("Unable to update API key record.")
        updated_key = await self.api_keys_collection.find_one({"_id": ObjectId(key_id)})
        return api_key_schema.APIKeyRecord(**api_key_serialize(updated_key))
    
    
    # Reset all API keys usage
    async def deactivate_all_api_keys(self) -> bool:
        await self.api_keys_collection.update_many(
            {"is_using": True},
            {"$set": {"is_using": False}}
        )
        return True


    # Delete an API key record
    async def delete_api_key(self, key_id: str) -> bool:
        result = await self.api_keys_collection.delete_one({"_id": ObjectId(key_id)})
        if result.deleted_count != 1:
            raise DatabaseException("Unable to delete API key record.")
        return True