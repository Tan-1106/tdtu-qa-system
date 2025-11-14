from bson import ObjectId
from datetime import datetime, timezone

from app.databases import mongo
from app.utils import serializer
from app.schemas import user_schema

# Read all users
async def get_users() -> list[user_schema.UserResponse]:
    users = []
    async for user in mongo.get_users_collection().find():
        users.append(user_schema.UserResponse(**serializer.user_serialize(user)))
    return users


# Read user by ID
async def get_user_by_id(user_id: str) -> user_schema.UserResponse:
    user = await mongo.get_users_collection().find_one({"_id": ObjectId(user_id)})
    if not user:
        raise ValueError("User not found")
    return user_schema.UserResponse(**serializer.user_serialize(user))


# Get user by email
async def get_user_by_email(email: str) -> user_schema.UserResponse:
    user = await mongo.get_users_collection().find_one({"email": email})
    if not user:
        raise ValueError("User not found")
    return user_schema.UserResponse(**serializer.user_serialize(user))


# Create a new user
async def create_user(user: dict) -> user_schema.UserResponse:
    user["created_at"] = datetime.now(timezone.utc)
    
    existing_email = await mongo.get_users_collection().find_one({"email": user["email"]})
    if existing_email:
        raise ValueError("Email already exists")

    result = await mongo.get_users_collection().insert_one(user)
    
    created_user = await mongo.get_users_collection().find_one({"_id": result.inserted_id})
    return user_schema.UserResponse(**serializer.user_serialize(created_user))


# Update a user by ID
async def update_user(user_id: str, user_update: dict) -> user_schema.UserResponse:
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID")

    if "email" in user_update:
        existing_email = await mongo.get_users_collection().find_one({"email": user_update["email"], "_id": {"$ne": ObjectId(user_id)}})
        if existing_email:
            raise ValueError("Email already exists")

    user_update["updated_at"] = datetime.now(timezone.utc)
    result = await mongo.get_users_collection().update_one(
        {"_id": ObjectId(user_id)},
        {"$set": user_update}
    )
    if result.matched_count == 0:
        raise ValueError("User not found")

    updated_user = await mongo.get_users_collection().find_one({"_id": ObjectId(user_id)})
    return user_schema.UserResponse(**serializer.user_serialize(updated_user))


# Delete a user by ID
async def delete_user(user_id: str) -> bool:
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID")

    result = await mongo.get_users_collection().delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise ValueError("User not found")

    return True