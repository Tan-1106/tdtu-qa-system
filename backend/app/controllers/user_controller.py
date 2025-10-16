from fastapi.encoders import jsonable_encoder

from app.schemas import user_schema
from app.services import user_service

# Get all users
async def get_users():
    users = await user_service.get_users()
    return users

# Get a user by ID
async def get_user_by_id(user_id: str):
    user = await user_service.get_user_by_id(user_id)
    return user

# Get a user by email
async def get_user_by_email(email: str):
    user = await user_service.get_user_by_email(email)
    return user

# Update a user by ID
async def update_user(user_id: str, user_update: user_schema.UserInformationUpdate):
    user_update = jsonable_encoder(user_update)
    user_update = {k: v for k, v in user_update.items() if v is not None}

    updated_user = await user_service.update_user(user_id, user_update)
    return updated_user

# Delete a user by ID
async def delete_user(user_id: str):
    response = await user_service.delete_user(user_id)
    return response
