from app.services import user_service
from app.schemas import user_schema

# Get all users
async def get_users():
    users = await user_service.get_users()
    return users

# Get a user by ID
async def get_user_by_id(user_id: str):
    user = await user_service.get_user_by_id(user_id)
    return user

