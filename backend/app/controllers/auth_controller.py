from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from app.services import auth_service
from app.schemas import auth_schema, user_schema

# Register a new user
async def register(request: auth_schema.RegisterRequest):
    user_data = jsonable_encoder(request)
    user = await auth_service.register_user(user_data)
    return user

# Login user
async def login(request: auth_schema.LoginRequest):
    request = jsonable_encoder(request)
    response = await auth_service.authenticate_user(request)
    return response

# Get current user from token
async def get_current_user(current_user: user_schema.UserResponse = Depends(auth_service.get_current_user)):
    return current_user