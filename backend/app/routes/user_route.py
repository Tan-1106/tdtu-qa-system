from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder

from app.schemas import user_schema
from app.services import auth_service
from app.controllers import user_controller
from app.utils.api_response import api_response
from app.utils.basic_information import Role, Faculty


# --- ROUTERS ---
admin_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[
        Depends(auth_service.require_role([Role.ADMIN.value]))
    ]
)


faculty_manager_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[
        Depends(auth_service.require_role([Role.FACULTY_MANAGER.value]))
    ]
)


student_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[
        Depends(auth_service.require_role([Role.STUDENT.value]))
    ]
)


general_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[
        Depends(auth_service.get_current_user)
    ]
)


# --- ADMIN ROUTES ---
# Get list of users (with pagination)
@admin_router.get("/")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    role: str = Query(None),
    faculty: str = Query(None),
    banned: bool = Query(None)
):
    users = await user_controller.get_users(page, limit, role, faculty, banned)
    return api_response(
        status_code=200,
        message="Get users list successfully.",
        details=users
    )
    

# Get list of role options
@admin_router.get("/roles")
async def get_role_options():
    roles = [role.value for role in Role]
    return api_response(
        status_code=200,
        message="Get role options successfully.",
        details={"roles": roles}
    )
    

# Get all faculty options
@admin_router.get("/faculties")
async def get_faculty_options():
    faculties = [faculty.value.name for faculty in Faculty]
    return api_response(
        status_code=200,
        message="Get faculty options successfully.",
        details={"faculties": faculties}
    )
    
    
# Assign role admin to user
@admin_router.post("/{user_id}/assign-admin")
async def assign_admin(
    user_id: str
):
    response = await user_controller.assign_admin(user_id)
    return api_response(
        status_code=200,
        message="Assign admin role successfully.",
        details=response
    )

    
# Assign role faculty manager to user or change manager's faculty
@admin_router.post("/{user_id}/assign-faculty-manager")
async def assign_faculty_manager(
    user_id: str,
    assign_data: user_schema.AssignFacultySchema
):
    assign_data = jsonable_encoder(assign_data)
    response = await user_controller.assign_faculty_manager(user_id, assign_data["faculty"])
    return api_response(
        status_code=200,
        message="Assign faculty manager role successfully.",
        details=response
    )
    

# Assign role student to user or change student's faculty
@admin_router.post("/{user_id}/assign-student")
async def assign_student(
    user_id: str,
    assign_data: user_schema.AssignFacultySchema
):
    assign_data = jsonable_encoder(assign_data)
    response = await user_controller.assign_student(user_id, assign_data["faculty"])
    return api_response(
        status_code=200,
        message="Assign student role successfully.",
        details=response
    )
    
    
# Ban a user
@admin_router.patch("/{user_id}/ban")
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
@admin_router.patch("/{user_id}/unban")
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


# --- FACULTY MANAGER ROUTES ---
# Get list of students based on Admin's faculty (with pagination)
@faculty_manager_router.get("/students")
async def get_students(
    current_user = Depends(auth_service.get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    banned: bool = Query(None)
):
    current_user = jsonable_encoder(current_user)
    students = await user_controller.get_students(current_user["faculty"], page, limit, banned)
    return api_response(
        status_code=200,
        message="Get students list successfully.",
        details=students
    )
    

# Ban a student
@faculty_manager_router.patch("/students/{student_id}/ban")
async def ban_student(
    student_id: str,
    current_user = Depends(auth_service.get_current_user)
):
    current_user = jsonable_encoder(current_user)
    response = await user_controller.ban_user(student_id, current_user)
    return api_response(
        status_code=200,
        message="Student has been banned successfully.",
        details=response
    )
    
    
# Unban a student
@faculty_manager_router.patch("/students/{student_id}/unban")
async def unban_student(
    student_id: str,
    current_user = Depends(auth_service.get_current_user)
):
    current_user = jsonable_encoder(current_user)
    response = await user_controller.unban_user(student_id, current_user)
    return api_response(
        status_code=200,
        message="Student has been unbanned successfully.",
        details=response
    )
    

# --- STUDENT ROUTES ---


# --- GENERAL ROUTES ---
# Logout a user
@general_router.post("/logout")
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
    