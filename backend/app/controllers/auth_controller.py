from fastapi import Depends

from app.services import auth_service
from app.schemas import user_schema

# Register
async def register(user: dict):
    user = await auth_service.register_user(user)
    return user


# Login
async def login(request: dict):
    response = await auth_service.login(request)
    return response


# Get Current User
async def get_current_user(current_user: user_schema.UserResponse = Depends(auth_service.get_current_user)):
    return current_user


# Tokens Refresh
async def refresh_tokens(refresh_token: str):
    new_tokens = await auth_service.refresh_tokens(refresh_token)
    return new_tokens