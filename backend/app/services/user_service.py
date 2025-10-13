from app.daos import user_dao

# Get all users
async def get_users():
    users = await user_dao.get_users()
    return users

# Get a user by ID
async def get_user_by_id(user_id: str):
    user = await user_dao.get_user_by_id(user_id)
    return user