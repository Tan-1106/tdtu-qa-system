from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app.schemas import user_schema
from app.services import auth_service
from app.controllers import user_controller
from app.utils.api_response import api_response


# # --- ROUTERS ---
# admin_router = APIRouter(
#     prefix="/users",
#     tags=["Users"],
#     dependencies=[Depends(auth_service.require_role(["Admin"]))]
# )

# user_router = APIRouter(
#     prefix="/users",
#     tags=["Users"],
#     dependencies=[Depends(auth_service.get_current_user)]
# )


# # --- ADMIN ROUTES ---
# # Lấy danh sách người dùng
# @admin_router.get("/")
# async def get_users():
#     try:
#         users = await user_controller.get_users()
#         return api_response(
#             status_code=200,
#             message="Lấy danh sách người dùng thành công",
#             details=users
#         )
#     except Exception as e:
#         return api_response(
#             status_code=500,
#             message="Lỗi máy chủ",
#             details=str(e)
#         )


# # Tìm người dùng theo email
# @admin_router.post("/search")
# async def get_user_by_email(email: user_schema.EmailLookup):
#     try:
#         email = jsonable_encoder(email)
#         user = await user_controller.get_user_by_email(email["email"])
#         return api_response(
#                 status_code=200,
#                 message="Lấy thông tin người dùng thành công",
#                 details=user
#             )
#     except ValueError as e:
#         return api_response(
#             status_code=404,
#             message="Không tìm thấy người dùng",
#             details=str(e)
#         )
#     except Exception as e:
#         return api_response(
#             status_code=500,
#             message="Lỗi máy chủ",
#             details=str(e)
#         )


# # Lấy người dùng theo ID
# @admin_router.get("/{user_id}")
# async def get_user_by_id(user_id: str):
#     try:
#         user = await user_controller.get_user_by_id(user_id)
#         return api_response(
#                 status_code=200,
#                 message="Lấy thông tin người dùng thành công",
#                 details=user
#             )
#     except ValueError as e:
#         return api_response(
#             status_code=404,
#             message="Không tìm thấy người dùng",
#             details=str(e)
#         )
#     except Exception as e:
#         return api_response(
#             status_code=500,
#             message="Lỗi máy chủ",
#             details=str(e)
#         )


# # Cập nhật người dùng theo ID
# @admin_router.patch("/{user_id}")
# async def update_user(
#     user_id: str,
#     user_update: user_schema.UserInformationUpdate
# ):
#     try:
#         user_update = jsonable_encoder(user_update)
#         updated_user = await user_controller.update_user(user_id, user_update)
#         return api_response(
#                 status_code=200,
#                 message="Cập nhật người dùng thành công",
#                 details=updated_user
#             )
#     except ValueError as e:
#         return api_response(
#             status_code=404,
#             message="Không tìm thấy người dùng",
#             details=str(e)
#         )
#     except Exception as e:
#         return api_response(
#             status_code=500,
#             message="Lỗi máy chủ",
#             details=str(e)
#         )
        
        
# # Xóa người dùng theo ID
# @admin_router.delete("/{user_id}")
# async def delete_user(user_id: str):
#     try:
#         await user_controller.delete_user(user_id)
#         return api_response(
#                     status_code=200,
#                     message="Xóa người dùng thành công",
#                     details=None
#                 )
#     except ValueError as e:
#         return api_response(
#             status_code=404,
#             message="Không tìm thấy người dùng",
#             details=str(e)
#         )
#     except Exception as e:
#         return api_response(
#             status_code=500,
#             message="Lỗi máy chủ",
#             details=str(e)
#         )
        
        
# # Chặn người dùng theo ID
# # TODO
    
    
# # USER ROUTES    
# # Cập nhật thông tin người dùng hiện tại
# @user_router.patch("/me")
# async def update_current_user(
#     user_update: user_schema.UserInformationUpdate,
#     current_user: dict = Depends(auth_service.get_current_user)
# ):
#     try:
#         user_update = jsonable_encoder(user_update)
#         updated_user = await user_controller.update_user(current_user["_id"], user_update)
#         return api_response(
#                 status_code=200,
#                 message="Cập nhật thông tin người dùng thành công",
#                 details=updated_user
#             )
#     except Exception as e:
#         return api_response(
#             status_code=500,
#             message="Lỗi máy chủ",
#             details=str(e)
#         )
        

# # Đổi mật khẩu người dùng hiện tại
# # TODO