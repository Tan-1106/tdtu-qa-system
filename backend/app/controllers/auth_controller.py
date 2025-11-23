from fastapi import Depends

from app.schemas import user_schema
from app.services import auth_service


# Tạo tài khoản người dùng
async def register(user: dict):
    user = await auth_service.register_user(user)
    return user


# Đăng nhập
async def login(request: dict):
    response = await auth_service.login(request)
    return response


# Lấy thông tin người dùng hiện tại
async def get_current_user(current_user: user_schema.UserResponse = Depends(auth_service.get_current_user)):
    return current_user


# Làm mới tokens
async def refresh_tokens(refresh_token: str):
    new_tokens = await auth_service.refresh_tokens(refresh_token)
    return new_tokens