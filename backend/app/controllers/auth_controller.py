from fastapi import Depends

from app.schemas import user_schema
from app.services import auth_service
from app.utils import smtp


# Xử lý đăng nhập bằng ELIT
async def elit_login(code: str) -> dict:
    tokens_and_user = await auth_service.elit_login(code)
    return tokens_and_user

# # Lấy thông tin người dùng hiện tại
# async def get_current_user(current_user: user_schema.UserResponse = Depends(auth_service.get_current_user)):
#     return current_user


# # Làm mới tokens
# async def refresh_tokens(refresh_token: str):
#     new_tokens = await auth_service.refresh_tokens(refresh_token)
#     return new_tokens