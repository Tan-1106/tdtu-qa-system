from fastapi import APIRouter, Depends

from app.controllers import auth_controller
from app.utils.api_response import api_response
from app.schemas import auth_schema, user_schema

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Register a new user
@router.post("/register")
async def register(request: auth_schema.RegisterRequest):
    try:
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
        
# Login user
@router.post("/login")
async def login(request: auth_schema.LoginRequest):
    try:
        token = await auth_controller.login(request)
        return api_response(
            status_code=200,
            message="User logged in successfully",
            details=token
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
        
# Get current user
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