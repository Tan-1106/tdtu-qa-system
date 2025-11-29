from app.daos import user_dao


# # Lấy tất cả người dùng
# async def get_users():
#     users = await user_dao.get_users()
#     return users


# # Lấy một người dùng theo ID
# async def get_user_by_id(user_id: str):
#     user = await user_dao.get_user_by_id(user_id)
#     if not user:
#         raise ValueError(f"Người dùng với ID {user_id} không tìm thấy")
#     return user


# # Lấy một người dùng theo email
# async def get_user_by_email(email: str):
#     user = await user_dao.get_user_by_email(email)
#     if not user:
#         raise ValueError(f"Người dùng với email {email} không tìm thấy")
#     return user


# # Lấy thông tin đăng nhập của người dùng theo email
# async def get_user_credentials_by_email(email: str):
#     user = await user_dao.get_user_credentials_by_email(email)
#     if not user:
#         raise ValueError(f"Người dùng với email {email} không tìm thấy")
#     return user


# # Cập nhật một người dùng theo ID
# async def update_user(user_id: str, user_update: dict):
#     updated_user = await user_dao.update_user(user_id, user_update)
#     if not updated_user:
#         raise ValueError(f"Người dùng với ID {user_id} không tìm thấy")
#     return updated_user


# # Xóa một người dùng theo ID
# async def delete_user(user_id: str):
#     result = await user_dao.delete_user(user_id)
#     if not result:
#         raise ValueError(f"Người dùng với ID {user_id} không tìm thấy")
#     return result