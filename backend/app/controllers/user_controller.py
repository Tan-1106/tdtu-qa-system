from app.services import user_service


# Lấy tất cả người dùng
async def get_users():
    users = await user_service.get_users()
    return users


# Lấy người dùng theo ID
async def get_user_by_id(user_id: str):
    user = await user_service.get_user_by_id(user_id)
    return user


# Lấy người dùng theo email
async def get_user_by_email(email: str):
    user = await user_service.get_user_by_email(email)
    return user


# Cập nhật người dùng theo ID
async def update_user(user_id: str, user_update: dict):
    user_update = {k: v for k, v in user_update.items() if v is not None}

    updated_user = await user_service.update_user(user_id, user_update)
    return updated_user


# Xóa người dùng theo ID
async def delete_user(user_id: str):
    response = await user_service.delete_user(user_id)
    return response
