from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app.controllers import auth_controller
from app.utils.api_response import api_response
from app.schemas import auth_schema, user_schema


# --- ROUTERS ---
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# --- ROUTES ---
# Xử lý Login Code từ ELIT
@router.post("/verify")
async def elit_login(code: auth_schema.ELITLoginCode):
    code = jsonable_encoder(code)["code"]
    try:
        tokens_and_user = await auth_controller.elit_login(code)
        return api_response(
            status_code=200,
            message="Đăng nhập thành công.",
            details=tokens_and_user
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message="Lỗi dữ liệu đầu vào.",
            details=str(e)
        )
        
            
# # Lấy thông tin người dùng hiện tại
# @router.get("/me")
# async def get_current_user(current_user: user_schema.UserResponse = Depends(auth_controller.get_current_user)):
#     try:
#         return api_response(
#             status_code=200,
#             message="Lấy thông tin người dùng hiện tại thành công.",
#             details=current_user
#         )
#     except Exception as e:
#         return api_response(
#             status_code=500,
#             message="Lỗi khi lấy thông tin người dùng hiện tại.",
#             details=str(e)
#         )
        
        
# # Làm mới Tokens
# @router.post("/refresh")
# async def refresh_tokens(refresh_token: auth_schema.RefreshToken):
#     try:
#         refresh_token = jsonable_encoder(refresh_token)["refresh_token"]
#         tokens = await auth_controller.refresh_tokens(refresh_token)
#         return api_response(
#             status_code=200,
#             message="Làm mới tokens thành công.",
#             details=tokens
#         )
#     except ValueError as e:
#         return api_response(
#             status_code=400,
#             message="Lỗi dữ liệu đầu vào.",
#             details=str(e)
#         )
#     except Exception as e:
#         return api_response(
#             status_code=500,
#             message="Lỗi máy chủ.",
#             details=str(e)
#         )