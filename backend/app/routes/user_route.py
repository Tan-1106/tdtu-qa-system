from fastapi import APIRouter
from app.utils.api_response import api_response
from app.controllers import user_controller

router = APIRouter(prefix="/users", tags=["Users"])

# Get all users
@router.get("/")
async def get_users():
    try:
        users = await user_controller.get_users()
        return api_response(
            status_code=200,
            message="Users retrieved successfully",
            details=users
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Internal Server Error",
            details=str(e)
        )
        
# Get a user by ID
@router.get("/{user_id}")
async def get_user_by_id(user_id: str):
    try:
        user = await user_controller.get_user_by_id(user_id)
        if user:
            return api_response(
                status_code=200,
                message="User retrieved successfully",
                details=user
            )
        else:
            return api_response(
                status_code=404,
                message="User not found",
                details=None
            )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Internal Server Error",
            details=str(e)
        )