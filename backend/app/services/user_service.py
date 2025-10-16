from app.daos import user_dao

# Get all users
async def get_users():
    users = await user_dao.get_users()
    return users

# Get a user by ID
async def get_user_by_id(user_id: str):
    user = await user_dao.get_user_by_id(user_id)
    return user

# Get a user by email
async def get_user_by_email(email: str):
    user = await user_dao.get_user_by_email(email)
    return user

# Update a user by ID
async def update_user(user_id: str, user_update: dict):
    updated_user = await user_dao.update_user(user_id, user_update)
    return updated_user

# Delete a user by ID
async def delete_user(user_id: str):
    result = await user_dao.delete_user(user_id)
    return result