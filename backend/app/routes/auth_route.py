from http.client import HTTPException
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app.controllers import auth_controller
from app.utils.api_response import api_response
from app.schemas import auth_schema, user_schema

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# --- ROUTES ---
# Register
@router.post("/register")
async def register(request: auth_schema.RegisterRequest):
    try:
        request = jsonable_encoder(request)
        user = await auth_controller.register(request)
        return api_response(
            status_code=201,
            message="User registered successfully",
            details=user
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message=str(e),
            details=None
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Internal Server Error",
            details=str(e)
        )
        
        
# Login
@router.post("/login")
async def login(request: auth_schema.LoginRequest):
    try:
        request = jsonable_encoder(request)
        tokens = await auth_controller.login(request)
        return api_response(
            status_code=200,
            message="User logged in successfully",
            details=tokens
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message=str(e),
            details=None
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Internal Server Error",
            details=str(e)
        )
        
        
        
# Get Current User
@router.get("/me")
async def get_current_user(current_user: user_schema.UserResponse = Depends(auth_controller.get_current_user)):
    try:
        return api_response(
            status_code=200,
            message="Current user fetched successfully",
            details=current_user
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Failed to fetch current user",
            details=str(e)
        )
        
        
# Refresh Access Token
@router.post("/refresh")
async def refresh_access_token(refresh_token: auth_schema.RefreshToken):
    try:
        refresh_token = jsonable_encoder(refresh_token)["refresh_token"]
        tokens = await auth_controller.refresh_tokens(refresh_token)
        return api_response(
            status_code=200,
            message="Current user fetched successfully",
            details=tokens
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message=str(e),
            details=None
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e),
            details=None
        )
    