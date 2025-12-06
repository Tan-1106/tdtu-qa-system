from app.services import user_service, auth_service
from app.utils.basic_information import Role, Faculty
from app.utils.api_response import UserError, AuthException

# Get list of users
async def get_users(
    page: int,
    limit: int,
    role: str = None,
    faculty: str = None,
    banned: bool = None,
    keyword: str = None,
    current_user: dict = None
):
    if role and role not in [r.value for r in Role]:
        raise UserError("Invalid role specified.")
    if faculty and faculty not in [fac.value.name for fac in Faculty]:
        raise UserError("Invalid faculty specified.")
    if keyword and not isinstance(keyword, str):
        raise UserError("Invalid keyword specified.")
    if current_user["role"] == Role.STUDENT.value:
        raise AuthException("Students are not allowed to view user list.")
    
    if current_user["role"] == Role.ADMIN.value:
        users = await user_service.get_users(page, limit, role, faculty, banned, keyword)
        return users
    
    elif (current_user["role"] == Role.FACULTY_MANAGER.value):
        users = await user_service.get_students(page, limit, current_user["faculty"], banned, keyword)
        return users
    
    return {"users": [], "total": 0, "total_pages": 0, "current_page": page}


# Assign admin role to user
async def assign_admin(user_id: str):
    response = await user_service.assign_admin(user_id)
    return response


# Assign faculty manager role to user
async def assign_faculty_manager(user_id: str, faculty: str):
    if faculty not in [fac.value.name for fac in Faculty]:
        raise UserError("Invalid faculty specified")
    
    response = await user_service.assign_faculty_manager(user_id, faculty)
    return response
    

# Assign student role to user
async def assign_student(user_id: str, faculty: str):
    if faculty not in [fac.value.name for fac in Faculty]:
        raise UserError("Invalid faculty specified")
    
    response = await user_service.assign_student(user_id, faculty)
    return response


# Ban a user
async def ban_user(user_id: str, current_user: dict):
    if current_user["_id"] == user_id:
        raise UserError("You cannot ban yourself")
    
    user_to_ban = await user_service.get_user_by_id(user_id)
    if user_to_ban["banned"]:
        raise UserError("User is already banned")
    
    if (current_user["role"] != Role.ADMIN.value):
        raise AuthException("You do not have permission to ban this user")
        
    response = await user_service.ban_user(user_id)
    return response


# Unban a user
async def unban_user(
    user_id: str,
    current_user: dict
):
    if current_user["_id"] == user_id:
        raise UserError("You cannot unban yourself")
    
    user_to_unban = await user_service.get_user_by_id(user_id)
    if not user_to_unban["banned"]:
        raise UserError("User is not banned")
    
    if (current_user["role"] != Role.ADMIN.value):
        raise AuthException("You do not have permission to unban this user")
    
    response = await user_service.unban_user(user_id)
    return response


# Logout user by revoking refresh token
async def logout_user(refresh_token: str):
    await auth_service.revoke_refresh_token(refresh_token)