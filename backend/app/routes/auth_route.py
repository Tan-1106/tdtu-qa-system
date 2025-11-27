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
# Đăng ký tài khoản mới
@router.post("/register")
async def register(request: auth_schema.RegisterRequest):
    try:
        request = jsonable_encoder(request)
        user = await auth_controller.register(request)
        return api_response(
            status_code=201,
            message="Đăng ký tài khoản thành công.",
            details=user
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message="Lỗi dữ liệu đầu vào.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
        
        
# Đăng nhập
@router.post("/login")
async def login(request: auth_schema.LoginRequest):
    try:
        request = jsonable_encoder(request)
        tokens = await auth_controller.login(request)
        return api_response(
            status_code=200,
            message="Đăng nhập thành công.",
            details=tokens
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message="Lỗi dữ liệu đầu vào.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
        

# Gửi yêu cầu reset mật khẩu
@router.post("/forgot-password")
async def forgot_password(request: auth_schema.ForgotPasswordRequest):
    try:
        request = jsonable_encoder(request)
        await auth_controller.forgot_password(request['email'])
        return api_response(
            status_code=200,
            message="Yêu cầu đặt lại mật khẩu đã được gửi thành công nếu email tồn tại trong hệ thống.",
            details=None
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )
        
            
# Lấy thông tin người dùng hiện tại
@router.get("/me")
async def get_current_user(current_user: user_schema.UserResponse = Depends(auth_controller.get_current_user)):
    try:
        return api_response(
            status_code=200,
            message="Lấy thông tin người dùng hiện tại thành công.",
            details=current_user
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi khi lấy thông tin người dùng hiện tại.",
            details=str(e)
        )
        
        
# Làm mới Tokens
@router.post("/refresh")
async def refresh_tokens(refresh_token: auth_schema.RefreshToken):
    try:
        refresh_token = jsonable_encoder(refresh_token)["refresh_token"]
        tokens = await auth_controller.refresh_tokens(refresh_token)
        return api_response(
            status_code=200,
            message="Làm mới tokens thành công.",
            details=tokens
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message="Lỗi dữ liệu đầu vào.",
            details=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Lỗi máy chủ.",
            details=str(e)
        )