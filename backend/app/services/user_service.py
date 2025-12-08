from fastapi.encoders import jsonable_encoder

from app.daos.user_dao import UserDAO


# Get user by ID
async def get_user_by_id(user_id: str):
    user = await UserDAO().get_user_by_id(user_id)
    return jsonable_encoder(user)


# Get list of users
async def get_users(
    page: int,
    limit: int,
    role: str = None,
    is_faculty_manager: bool = None,
    faculty: str = None,
    banned: bool = None,
    keyword: str = None
):
    skip = (page - 1) * limit
    total = await UserDAO().count_all_users(role, is_faculty_manager, faculty, banned, keyword)
    total_pages = (total + limit - 1) // limit
    users = await UserDAO().get_users(skip, limit, role, is_faculty_manager, faculty, banned, keyword)
    return {
        "users": jsonable_encoder(users),
        "total": total,
        "total_pages": total_pages,
        "current_page": page
    }


# Get list of students
async def get_faculty_users(
    page: int,
    limit: int,
    role: str,
    faculty: str,
    banned: bool = None,
    keyword: str = None
):
    skip = (page - 1) * limit
    total = await UserDAO().count_faculty_users(role, faculty, banned, keyword)
    total_pages = (total + limit - 1) // limit
    users = await UserDAO().get_faculty_users(role, faculty, skip, limit, banned, keyword)
    return {
        "users": jsonable_encoder(users),
        "total": total,
        "total_pages": total_pages,
        "current_page": page
    }
    
    
# Get all existing faculty options
async def get_all_existing_faculties():
    faculties = await UserDAO().get_all_existing_faculties()
    return jsonable_encoder(faculties)


# Assign admin role to user
async def assign_admin(user_id: str):
    updated_user = await UserDAO().assign_admin_role(user_id)
    return jsonable_encoder(updated_user)

    
# Assign teacher role to user
async def assign_teacher(user_id: str, faculty: str):
    updated_user = await UserDAO().assign_teacher_role(user_id, faculty)
    return jsonable_encoder(updated_user)


# Assign student role to user
async def assign_student(user_id: str, faculty: str):
    updated_user = await UserDAO().assign_student_role(user_id, faculty)
    return jsonable_encoder(updated_user)


# Assign faculty manager permission to user
async def assign_faculty_manager(user_id: str, faculty: str):
    updated_user = await UserDAO().assign_faculty_manager_role(user_id, faculty)
    return jsonable_encoder(updated_user)


# Revoke faculty manager permission from user
async def revoke_permissions(user_id: str):
    updated_user = await UserDAO().revoke_permissions(user_id)
    return jsonable_encoder(updated_user)

# Ban a user
async def ban_user(user_id: str):
    response = await UserDAO().ban_user(user_id)
    return jsonable_encoder(response)


# Unban a user
async def unban_user(user_id: str):
    response = await UserDAO().unban_user(user_id)
    return jsonable_encoder(response)