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
    async def count_all_api_keys(self) -> int:
        count = await self.api_keys_collection.count_documents({})
        return count
    
    
    # Get all API keys
    async def get_all_api_keys(self) -> list[api_key_schema.APIKeyRecord]:
        api_keys = []
        cursor = self.api_keys_collection.find()
        async for key in cursor:
            api_keys.append(api_key_schema.APIKeyRecord(**api_key_serialize(key)))
        return api_keys
    
    
    # Get all API keys (Pagination)
    async def get_api_keys(self, skip: int, limit: int) -> list[api_key_schema.APIKeyRecord]:
        api_keys = []
        cursor = self.api_keys_collection.find().skip(skip).limit(limit)
        async for key in cursor:
            api_keys.append(api_key_schema.APIKeyRecord(**api_key_serialize(key)))
        return api_keys
        
        
    # Get a single API key by ID
    async def get_api_key_by_id(self, key_id: str) -> dict | None:
        api_key = await self.api_keys_collection.find_one({"_id": ObjectId(key_id)})
        if api_key:
            return api_key_schema.APIKeyRecord(**api_key_serialize(api_key))
        return None
    

    # Update an existing API key record
    async def update_api_key(self, key_id: str, update_data: dict) -> dict:
        print("Updating API Key ID:", key_id, "with data:", update_data)
        update_data["updated_at"] = datetime.now(timezone.utc)
        result = await self.api_keys_collection.update_one(
            {"_id": ObjectId(key_id)},
            {"$set": update_data}
        )
        if result.modified_count != 1:
            raise DatabaseException("Unable to update API key record.")
        updated_key = await self.api_keys_collection.find_one({"_id": ObjectId(key_id)})
        print("Updated API Key Record:", updated_key)
        return api_key_schema.APIKeyRecord(**api_key_serialize(updated_key))
    
    
    # Reset all API keys usage
    async def reset_all_api_keys_usage(self) -> bool:
        result = await self.api_keys_collection.update_many(
            {"is_using": True},
            {"$set": {"is_using": False, "using_model": None}}
        )
        return True


    # Delete an API key record
    async def delete_api_key(self, key_id: str) -> bool:
        result = await self.api_keys_collection.delete_one({"_id": ObjectId(key_id)})
        if result.deleted_count != 1:
            raise DatabaseException("Unable to delete API key record.")
        return True
    
    
    # Toggle API key usage status
    async def toggle_api_key_status(self, key_id: str, using_model: str | None = None) -> dict:
        api_key = await self.api_keys_collection.find_one({"_id": ObjectId(key_id)})
        if not api_key:
            raise DatabaseException("API key not found.")
        
        new_status = not api_key.get("is_using", True)
        print("Toggling API Key ID:", key_id, "to status:", new_status, "with model:", using_model)
        if new_status is False:
            result = await self.api_keys_collection.update_one(
                {"_id": ObjectId(key_id)},
                {"$set": {"is_using": new_status, "using_model": None}}
            )
        else:
            await self.api_keys_collection.update_many(
                {"is_using": True},
                {"$set": {"is_using": False, "using_model": None}}
            )
            result = await self.api_keys_collection.update_one(
                {"_id": ObjectId(key_id)},
                {"$set": {"is_using": new_status, "using_model": using_model}}
            )
        
        if result.modified_count != 1:
            raise DatabaseException("Unable to toggle API key status.")
        
        updated_key = await self.api_keys_collection.find_one({"_id": ObjectId(key_id)})
        return api_key_schema.APIKeyRecord(**api_key_serialize(updated_key))