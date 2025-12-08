from bson import ObjectId
from datetime import datetime, timezone

from app.databases import mongo
from app.utils import serializer
from app.schemas import user_schema
from app.utils.basic_information import Role
from app.utils.api_response import DatabaseException


class UserDAO:
    def __init__(self):
        self.users_collection = mongo.get_users_collection()


    # Create a new user or return existing user
    async def create_user(self, user: dict) -> user_schema.UserRecord:
        role_map = {
            "is_admin": Role.ADMIN.value,
            "is_teacher": Role.TEACHER.value,
            "is_student": Role.STUDENT.value,
        }
        role = next(
            (value for key, value in role_map.items() if user.get(key)),
            ""
        )

        # Check if user already exists and check user system role assignment
        existing_user = await self.users_collection.find_one({"sub": user["sub"]})
        
        if existing_user and existing_user.get("system_role_assigned"):
            return user_schema.UserRecord(**serializer.user_serialize(existing_user))
        elif existing_user and not existing_user.get("system_role_assigned"):
            user_update = {
                "role": role,
                "faculty": user["faculty"],
                "is_faculty_manager": user["is_faculty_manager"]
            }
            await self.users_collection.update_one({"_id": existing_user["_id"]}, {"$set": user_update})
            updated_user = await self.users_collection.find_one({"_id": existing_user["_id"]})
            return user_schema.UserRecord(**serializer.user_serialize(updated_user))
        
        new_user_record = {
            "sub": user["sub"],
            "name": user["name"],
            "email": user["email"],
            "image": user["image"],
            "role": role,
            "faculty": user["faculty"],
            "is_faculty_manager": user["is_faculty_manager"],
            "system_role_assigned": False,
            "banned": False,
            "created_at": datetime.now(timezone.utc)
        }
        
        result = await self.users_collection.insert_one(new_user_record)
        created_user = await self.users_collection.find_one({"_id": result.inserted_id})
        if not created_user:
            raise DatabaseException("Failed to create user")
            
        return user_schema.UserRecord(**serializer.user_serialize(created_user))
        
    
    # Count all users
    async def count_all_users(self, role: str = None, is_faculty_manager: bool = None, faculty: str = None, banned: bool = None, keyword: str = None) -> int:
        query = {}
        if role:
            query["role"] = role
        if is_faculty_manager is not None:
            query["is_faculty_manager"] = is_faculty_manager
        if faculty:
            query["faculty"] = faculty
        if banned is not None:
            query["banned"] = banned
        if keyword:
            query["$or"] = [
            {"name": {"$regex": keyword, "$options": "i"}},
            {"sub": {"$regex": keyword, "$options": "i"}}
        ]
            
        count = await self.users_collection.count_documents(query)
        return count
    
    
    # Get all users
    async def get_users(self, skip: int, limit: int, role: str = None, is_faculty_manager: bool = None, faculty: str = None, banned: bool = None, keyword: str = None) -> list[user_schema.UserRecord]:
        users = []
        query = {}
        if role:
            query["role"] = role
        if is_faculty_manager is not None:
            query["is_faculty_manager"] = is_faculty_manager
        if faculty:
            query["faculty"] = faculty
        if banned is not None:
            query["banned"] = banned
        if keyword:
            query["$or"] = [
            {"name": {"$regex": keyword, "$options": "i"}},
            {"sub": {"$regex": keyword, "$options": "i"}}
        ]
            
        cursor = self.users_collection.find(query).skip(skip).limit(limit)
        async for user in cursor:
            users.append(user_schema.UserRecord(**serializer.user_serialize(user)))
        return users
    
    
    # Get all existing faculty options
    async def get_all_existing_faculties(self) -> list[str]:
        faculties = await self.users_collection.distinct("faculty", {"faculty": {"$ne": None}})
        return faculties
    
    
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
    async def count_faculty_users(self, role: str, faculty: str, banned: bool = None, keyword: str = None) -> int:
        query = {"faculty": faculty, "is_faculty_manager": False}
        if role is not None:
            query["role"] = role
        if banned is not None:
            query["banned"] = banned
        if keyword:
            query["$or"] = [
            {"name": {"$regex": keyword, "$options": "i"}},
            {"sub": {"$regex": keyword, "$options": "i"}}
        ]
            
        count = await self.users_collection.count_documents(query)
        return count
    
    
    # Get students by faculty with pagination
    async def get_faculty_users(self, role: str, faculty: str, skip: int, limit: int, banned: bool = None, keyword: str = None) -> list[user_schema.UserRecord]:
        users = []
        query = {"faculty": faculty, "is_faculty_manager": False}
        if role is not None:
            query["role"] = role
        if banned is not None:
            query["banned"] = banned
        if keyword:
            query["$or"] = [
            {"name": {"$regex": keyword, "$options": "i"}},
            {"sub": {"$regex": keyword, "$options": "i"}}
        ]
            
        cursor = self.users_collection.find(query).skip(skip).limit(limit)
        async for user in cursor:
            users.append(user_schema.UserRecord(**serializer.user_serialize(user)))
        return users


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
            {"$set": {"role": Role.ADMIN.value, "faculty": None, "is_faculty_manager": False, "system_role_assigned": True}}
        )
        if result.matched_count == 0:
            raise DatabaseException("User not found")
        updated_user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        return user_schema.UserRecord(**serializer.user_serialize(updated_user))
    
    # Assign teacher role to user
    async def assign_teacher_role(self, user_id: str, faculty: str) -> user_schema.UserRecord:
        result = await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": Role.TEACHER.value, "faculty": faculty, "system_role_assigned": True}}
        )
        if result.matched_count == 0:
            raise DatabaseException("User not found")
        updated_user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        return user_schema.UserRecord(**serializer.user_serialize(updated_user))
    
    
    # Assign student role to user
    async def assign_student_role(self, user_id: str, faculty: str) -> user_schema.UserRecord:
        result = await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": Role.STUDENT.value, "faculty": faculty, "system_role_assigned": True}}
        )
        if result.matched_count == 0:
            raise DatabaseException("User not found")
        updated_user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        return user_schema.UserRecord(**serializer.user_serialize(updated_user))
    
    
    # Assign faculty manager role to user
    async def assign_faculty_manager_role(self, user_id: str, faculty: str) -> user_schema.UserRecord:
        result = await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"faculty": faculty, "is_faculty_manager": True,  "system_role_assigned": True}}
        )
        if result.matched_count == 0:
            raise DatabaseException("User not found")
        updated_user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        return user_schema.UserRecord(**serializer.user_serialize(updated_user))
    
    
    # Revoke faculty manager role from user
    async def revoke_permissions(self, user_id: str) -> user_schema.UserRecord:
        result = await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_faculty_manager": False, "system_role_assigned": False}}
        )
        if result.matched_count == 0:
            raise DatabaseException("User not found")
        updated_user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
        return user_schema.UserRecord(**serializer.user_serialize(updated_user))