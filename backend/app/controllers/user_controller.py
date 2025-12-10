from app.services import user_service, auth_service
from app.utils.basic_information import Role
from app.utils.api_response import UserError, AuthException

# Get list of users
async def get_users(
    page: int,
    limit: int,
    role: str = None,
    is_faculty_manager: bool = None,
    faculty: str = None,
    banned: bool = None,
    keyword: str = None,
    current_user: dict = None
):
    print("Current User in Controller:", current_user)
    if role and role not in [r.value for r in Role]:
        raise UserError("Invalid role specified.")
    if faculty and faculty not in await user_service.get_all_existing_faculties():
        raise UserError("Invalid faculty specified.")
    if keyword and not isinstance(keyword, str):
        raise UserError("Invalid keyword specified.")
    if current_user["role"] != Role.ADMIN.value and not current_user["is_faculty_manager"]:
        raise AuthException("You do not have permission to access the users list.")
    
    if current_user["role"] == Role.ADMIN.value:
        users = await user_service.get_users(page, limit, role, is_faculty_manager, faculty, banned, keyword)
        return users
    elif (current_user["is_faculty_manager"]) and current_user["faculty"] is not None and is_faculty_manager is None:
        users = await user_service.get_faculty_users(page, limit, role, current_user["faculty"], banned, keyword)
        return users
    else:
        raise AuthException("You do not have permission to access the users list.")
    

# Get all existing faculty options
async def get_all_existing_faculties():
    faculties = await user_service.get_all_existing_faculties()
    return faculties


# Assign admin role to user
async def assign_admin(user_id: str):
    response = await user_service.assign_admin(user_id)
    return response


# Assign teacher role to user
async def assign_teacher(user_id: str, faculty: str, current_user: dict):
    if faculty and faculty not in await user_service.get_all_existing_faculties():
        raise UserError("Invalid faculty specified.")
    user_to_assign = await user_service.get_user_by_id(user_id)
    if current_user["role"] != Role.ADMIN.value:
        raise AuthException("You do not have permission to assign teacher role.")
    if user_to_assign["_id"] == current_user["_id"]:
        raise UserError("You cannot assign role to yourself.")
    
    response = await user_service.assign_teacher(user_id, faculty)
    return response
    

# Assign student role to user
async def assign_student(user_id: str, faculty: str, current_user: dict):
    if faculty and faculty not in await user_service.get_all_existing_faculties():
        raise UserError("Invalid faculty specified.")
    user_to_assign = await user_service.get_user_by_id(user_id)
    if current_user["role"] != Role.ADMIN.value:
        raise AuthException("You do not have permission to assign student role.")
    if user_to_assign["_id"] == current_user["_id"]:
        raise UserError("You cannot assign role to yourself.")
    
    response = await user_service.assign_student(user_id, faculty)
    return response


# Assign faculty manager permission to user
async def assign_faculty_manager(user_id: str, faculty: str, current_user: dict):
    if faculty and faculty not in await user_service.get_all_existing_faculties():
        raise UserError("Invalid faculty specified.")
    user_to_assign = await user_service.get_user_by_id(user_id)
    if current_user["role"] != Role.ADMIN.value:
        raise AuthException("You do not have permission to assign faculty manager role.")
    if user_to_assign["_id"] == current_user["_id"]:
        raise UserError("You cannot assign role to yourself.")
    
    response = await user_service.assign_faculty_manager(user_id, faculty)
    return response


# Revoke faculty manager permission from user
async def revoke_permissions(user_id: str, current_user: dict):
    user_to_revoke = await user_service.get_user_by_id(user_id)
    if current_user["role"] != Role.ADMIN.value:
        raise AuthException("You do not have permission to revoke this user's permissions.")
    if user_to_revoke["_id"] == current_user["_id"]:
        raise UserError("You cannot revoke your own permissions.")
    
    permissions_revoked = await user_service.revoke_permissions(user_id)
    tokens_revoked = await auth_service.revoke_all_tokens_of_user(user_to_revoke["sub"])
    
    return permissions_revoked and tokens_revoked


# Ban a user
async def ban_user(user_id: str, current_user: dict):
    if current_user["_id"] == user_id:
        raise UserError("You cannot ban yourself")
    
    if (current_user["role"] != Role.ADMIN.value):
        raise AuthException("You do not have permission to ban this user")
    
    user_to_ban = await user_service.get_user_by_id(user_id)
    if user_to_ban["banned"]:
        raise UserError("User is already banned")
        
    response = await user_service.ban_user(user_id)
    return response


# Unban a user
async def unban_user(
    user_id: str,
    current_user: dict
):
    if current_user["_id"] == user_id:
        raise UserError("You cannot unban yourself")
    
    if (current_user["role"] != Role.ADMIN.value):
        raise AuthException("You do not have permission to unban this user")
    
    user_to_unban = await user_service.get_user_by_id(user_id)
    if not user_to_unban["banned"]:
        raise UserError("User is not banned")
    
    response = await user_service.unban_user(user_id)
    return response


# Logout user by revoking refresh token
async def logout_user(refresh_token: str):
    await auth_service.revoke_refresh_token(refresh_token)