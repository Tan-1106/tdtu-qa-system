from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder

from app.schemas import user_schema
from app.services import auth_service
from app.controllers import user_controller
from app.utils.basic_information import Role
from app.utils.api_response import api_response

# --- ROUTER ---
router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(auth_service.get_current_user)]
)


# --- ROUTES ---
# Get list of users (with pagination)
@router.get("/")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    role: str = Query(None),
    is_faculty_manager: bool = Query(None),                 # Admin only
    faculty: str = Query(None),                             # Admin only
    banned: bool = Query(None),
    keyword: str = Query(None),
    current_user = Depends(auth_service.get_current_user)
):
    current_user = jsonable_encoder(current_user)
    users = await user_controller.get_users(page, limit, role, is_faculty_manager, faculty, banned, keyword, current_user)
    return api_response(
        status_code=200,
        message="Get users list successfully.",
        details=users
    )
    

# Get list of role options
@router.get("/roles")
async def get_role_options(
    check_admin = Depends(auth_service.require_role([Role.ADMIN.value]))
):
    roles = [role.value for role in Role]
    return api_response(
        status_code=200,
        message="Get role options successfully.",
        details={"roles": roles}
    )
    

# Get all existing faculty options
@router.get("/faculties")
async def get_faculty_options(
    check_admin = Depends(auth_service.require_role([Role.ADMIN.value]))
):
    faculties = await user_controller.get_all_existing_faculties()
    return api_response(
        status_code=200,
        message="Get faculty options successfully.",
        details={"faculties": faculties}
    )
    
    
# Assign role admin to user
@router.post("/{user_id}/assign-admin")
async def assign_admin(
    user_id: str,
    check_admin = Depends(auth_service.require_role([Role.ADMIN.value]))
):
    response = await user_controller.assign_admin(user_id)
    return api_response(
        status_code=200,
        message="Assign admin role successfully.",
        details=response
    )

    
# Assign role teacher to user
@router.post("/{user_id}/assign-teacher")
async def assign_teacher(
    user_id: str,
    assign_data: user_schema.AssignFacultySchema,
    current_user = Depends(auth_service.get_current_user)
):
    assign_data = jsonable_encoder(assign_data)
    current_user = jsonable_encoder(current_user)
    response = await user_controller.assign_teacher(user_id, assign_data["faculty"], current_user)
    return api_response(
        status_code=200,
        message="Assign teacher role successfully.",
        details=response
    )
    

# Assign role student to user or change student's faculty
@router.post("/{user_id}/assign-student")
async def assign_student(
    user_id: str,
    assign_data: user_schema.AssignFacultySchema,
    current_user = Depends(auth_service.get_current_user)
):
    assign_data = jsonable_encoder(assign_data)
    current_user = jsonable_encoder(current_user)
    response = await user_controller.assign_student(user_id, assign_data["faculty"], current_user)
    return api_response(
        status_code=200,
        message="Assign student role successfully.",
        details=response
    )
    

# Assign faculty manager permission to user
@router.post("/{user_id}/assign-faculty-manager")
async def assign_faculty_manager(
    user_id: str,
    assign_data: user_schema.AssignFacultySchema,
    current_user = Depends(auth_service.get_current_user)
):
    assign_data = jsonable_encoder(assign_data)
    current_user = jsonable_encoder(current_user)
    response = await user_controller.assign_faculty_manager(user_id, assign_data["faculty"], current_user)
    return api_response(
        status_code=200,
        message="Assign faculty manager role successfully.",
        details=response
    )
    
    
# Revoke system-granted permissions from user
@router.post("/{user_id}/revoke-permissions")
async def revoke_permissions(
    user_id: str,
    current_user = Depends(auth_service.get_current_user)
):
    response = await user_controller.revoke_permissions(user_id, current_user)
    return api_response(
        status_code=200,
        message="Revoke permissions successfully.",
        details=response
    )
    
    
# Ban a user
@router.patch("/{user_id}/ban")
async def ban_user(
    user_id: str,
    current_user = Depends(auth_service.get_current_user)
):
    current_user = jsonable_encoder(current_user)
    response = await user_controller.ban_user(user_id, current_user)
    return api_response(
        status_code=200,
        message="User has been banned successfully.",
        details=response
    )
    

# Unban a user
@router.patch("/{user_id}/unban")
async def unban_user(
    user_id: str,
    current_user = Depends(auth_service.get_current_user)
):
    current_user = jsonable_encoder(current_user)
    response = await user_controller.unban_user(user_id, current_user)
    return api_response(
        status_code=200,
        message="User has been unbanned successfully.",
        details=response
    )


# --- GENERAL ROUTES ---
# Logout a user
@router.post("/logout")
async def logout_user(
    refresh_token: user_schema.LogoutRequest
):
    refresh_token = jsonable_encoder(refresh_token)["refresh_token"]
    await user_controller.logout_user(refresh_token)
    return api_response(
        status_code=200,
        message="User logged out successfully.",
        details=None
    )