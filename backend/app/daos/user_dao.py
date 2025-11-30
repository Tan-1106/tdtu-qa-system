from bson import ObjectId
from datetime import datetime, timezone

from app.databases import mongo
from app.utils import serializer
from app.schemas import user_schema
from app.utils.user_information import Role
from app.utils.api_response import DatabaseException


class UserDAO:
    def __init__(self):
        self.users_collection = mongo.get_users_collection()


    # Create a new user or return existing user
    async def create_user(self, user: dict) -> user_schema.UserRecord:
        existing_user = await self.users_collection.find_one({"email": user["email"]})
        if existing_user:
            return user_schema.UserRecord(**serializer.user_serialize(existing_user))

        user["banned"] = False
        user["created_at"] = datetime.now(timezone.utc)
        result = await self.users_collection.insert_one(user)
        created_user = await self.users_collection.find_one({"_id": result.inserted_id})
        
        return user_schema.UserRecord(**serializer.user_serialize(created_user))
    
    
    # Count all users
    async def count_all_users(self) -> int:
        count = await self.users_collection.count_documents({})
        return count
    
    
    # Get all users
    async def get_users(self, skip: int, limit: int) -> list[user_schema.UserRecord]:
        users = []
        cursor = self.users_collection.find().skip(skip).limit(limit)
        async for user in cursor:
            users.append(user_schema.UserRecord(**serializer.user_serialize(user)))
        return users
    
    
    # Get user by id
    async def get_user_by_id(self, user_id: str) -> user_schema.UserRecord:
        user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise DatabaseException("User not found")
        return user_schema.UserRecord(**serializer.user_serialize(user))
    
    
    # Get user by sub
    async def get_user_by_sub(self, user_sub: str) -> user_schema.UserRecord:
        user = await self.users_collection.find_one({"sub": user_sub})
        if not user:
            raise DatabaseException("User not found")
        return user_schema.UserRecord(**serializer.user_serialize(user))
    
    
    # Count students by faculty
    async def count_students_by_faculty(self, faculty: str) -> int:
        count = await self.users_collection.count_documents({"faculty": faculty, "role": Role.STUDENT.value})
        return count
    
    
    # Get students by faculty with pagination
    async def get_students_by_faculty(self, faculty: str, skip: int, limit: int) -> list[user_schema.UserRecord]:
        students = []
        cursor = self.users_collection.find({"faculty": faculty, "role": Role.STUDENT.value}).skip(skip).limit(limit)
        async for user in cursor:
            students.append(user_schema.UserRecord(**serializer.user_serialize(user)))
        return students


    # Ban a user by id
    async def ban_user(self, user_id: str) -> bool:
        result = await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"banned": True}}
        )
        if result.matched_count == 0:
            raise DatabaseException("User not found")
        updated_user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        return user_schema.UserRecord(**serializer.user_serialize(updated_user))
    
    
    # Ban a user by sub
    async def ban_user_by_sub(self, user_sub: str) -> bool:
        result = await self.users_collection.update_one(
            {"sub": user_sub},
            {"$set": {"banned": True}}
        )
        if result.matched_count == 0:
            raise DatabaseException("User not found")
        updated_user = await self.users_collection.find_one({"sub": user_sub})
        return user_schema.UserRecord(**serializer.user_serialize(updated_user))
    
    
    # Unban a user by id
    async def unban_user(self, user_id: str) -> bool:
        result = await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"banned": False}}
        )
        if result.matched_count == 0:
            raise DatabaseException("User not found")
        updated_user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        return user_schema.UserRecord(**serializer.user_serialize(updated_user))
    
    
    # Unban a user by sub
    async def unban_user_by_sub(self, user_sub: str) -> bool:
        result = await self.users_collection.update_one(
            {"sub": user_sub},
            {"$set": {"banned": False}}
        )
        if result.matched_count == 0:
            raise DatabaseException("User not found")
        updated_user = await self.users_collection.find_one({"sub": user_sub})
        return user_schema.UserRecord(**serializer.user_serialize(updated_user))
    
    

    # Assign admin role to user
    async def assign_admin_role(self, user_id: str) -> user_schema.UserRecord:
        result = await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": Role.ADMIN.value, "faculty": "N/A"}}
        )
        if result.matched_count == 0:
            raise DatabaseException("User not found")
        updated_user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        return user_schema.UserRecord(**serializer.user_serialize(updated_user))
    
    # Assign faculty manager role to user
    async def assign_faculty_manager_role(self, user_id: str, faculty: str) -> user_schema.UserRecord:
        result = await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": Role.FACULTY_MANAGER.value, "faculty": faculty}}
        )
        if result.matched_count == 0:
            raise DatabaseException("User not found")
        updated_user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        return user_schema.UserRecord(**serializer.user_serialize(updated_user))
    
    
    # Assign student role to user
    async def assign_student_role(self, user_id: str, faculty: str) -> user_schema.UserRecord:
        result = await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": Role.STUDENT.value, "faculty": faculty}}
        )
        if result.matched_count == 0:
            raise DatabaseException("User not found")
        updated_user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        return user_schema.UserRecord(**serializer.user_serialize(updated_user))