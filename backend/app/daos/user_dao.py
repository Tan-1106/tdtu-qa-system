from bson import ObjectId
from typing import Optional
from datetime import datetime, timezone
from app.databases import mongo
from app.utils import serializer
from app.schemas import user_schema

# Read all users
async def get_users():
    users = []
    async for user in mongo.get_users_collection().find():
        users.append(user_schema.UserResponse(**serializer.user_serialize(user)))
    return users

# Read user by ID
async def get_user_by_id(user_id: str) -> Optional[user_schema.UserResponse]:
    user = await mongo.get_users_collection().find_one({"_id": ObjectId(user_id)})
    if not user:
        raise ValueError("User not found")
    return user_schema.UserResponse(**serializer.user_serialize(user))

# Get user by email
async def get_user_by_email(email: str) -> Optional[user_schema.UserResponse]:
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