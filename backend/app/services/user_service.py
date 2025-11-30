from fastapi.encoders import jsonable_encoder
from app.daos.user_dao import UserDAO


# Get user by ID
async def get_user_by_id(user_id: str):
    user = await UserDAO().get_user_by_id(user_id)
    return jsonable_encoder(user)


# Get list of users
async def get_users(page: int, limit: int):
    skip = (page - 1) * limit
    total = await UserDAO().count_all_users()
    total_pages = (total + limit - 1) // limit
    users = await UserDAO().get_users(skip, limit)
    return {
        "users": jsonable_encoder(users),
        "total": total,
        "total_pages": total_pages,
        "current_page": page
    }


# Get list of students
async def get_students(faculty: str, page: int, limit: int):
    skip = (page - 1) * limit
    total = await UserDAO().count_students_by_faculty(faculty)
    total_pages = (total + limit - 1) // limit
    students = await UserDAO().get_students_by_faculty(faculty, skip, limit)
    return {
        "students": jsonable_encoder(students),
        "total": total,
        "total_pages": total_pages,
        "current_page": page
    }


# Assign admin role to user
async def assign_admin(user_id: str):
    updated_user = await UserDAO().assign_admin_role(user_id)
    return jsonable_encoder(updated_user)

    
# Assign faculty manager role to user
async def assign_faculty_manager(user_id: str, faculty: str):
    updated_user = await UserDAO().assign_faculty_manager_role(user_id, faculty)
    return jsonable_encoder(updated_user)


# Assign student role to user
async def assign_student(user_id: str, faculty: str):
    updated_user = await UserDAO().assign_student_role(user_id, faculty)
    return jsonable_encoder(updated_user)


# Ban a user
async def ban_user(user_id: str):
    response = await UserDAO().ban_user(user_id)
    return jsonable_encoder(response)


# Unban a user
async def unban_user(user_id: str):
    response = await UserDAO().unban_user(user_id)
    return jsonable_encoder(response)