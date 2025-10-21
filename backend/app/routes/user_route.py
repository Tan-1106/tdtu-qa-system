from fastapi import APIRouter, Depends
from app.utils.api_response import api_response

from app.schemas import user_schema
from app.services import auth_service
from app.controllers import user_controller

admin_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(auth_service.require_role(["Admin"]))]
)

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(auth_service.get_current_user)]
)

# ADMIN ROUTES
# Get all users
@admin_router.get("/")
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
@admin_router.get("/{user_id}")
async def get_user_by_id(user_id: str):
    try:
        user = await user_controller.get_user_by_id(user_id)
        return api_response(
                status_code=200,
                message="User retrieved successfully",
                details=user
            )
    except ValueError as e:
        return api_response(
            status_code=404,
            message=str(e),
            details=None
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Internal Server Error",
            details=str(e)
        )

# Search user by email
@admin_router.get("/search")
async def get_user_by_email(email: str):
    try:
        user = await user_controller.get_user_by_email(email)
        return api_response(
                status_code=200,
                message="User retrieved successfully",
                details=user
            )
    except ValueError as e:
        return api_response(
            status_code=404,
            message=str(e),
            details=None
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Internal Server Error",
            details=str(e)
        )
        
# Update a user by ID
@admin_router.patch("/{user_id}")
async def update_user(
    user_id: str,
    user_update: user_schema.UserInformationUpdate
):
    try:
        updated_user = await user_controller.update_user(user_id, user_update)
        return api_response(
                status_code=200,
                message="User updated successfully",
                details=updated_user
            )
    except ValueError as e:
        return api_response(
            status_code=404,
            message=str(e),
            details=None
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Internal Server Error",
            details=str(e)
        )
        
# Delete a user by ID
@admin_router.delete("/{user_id}")
async def delete_user(user_id: str):
    try:
        await user_controller.delete_user(user_id)
        return api_response(
                    status_code=200,
                    message="User deleted successfully",
                    details=None
                )
    except ValueError as e:
        return api_response(
            status_code=404,
            message=str(e),
            details=None
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Internal Server Error",
            details=str(e)
        )
    
# USER ROUTES    
# Update current user's information
@user_router.patch("/me")
async def update_current_user(
    user_update: user_schema.UserInformationUpdate,
    current_user: dict = Depends(auth_service.get_current_user)
):
    try:
        updated_user = await user_controller.update_user(current_user["_id"], user_update)
        return api_response(
                status_code=200,
                message="User information updated successfully",
                details=updated_user
            )
    except Exception as e:
        return api_response(
            status_code=500,
            message="Internal Server Error",
            details=str(e)
        )