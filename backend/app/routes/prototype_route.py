from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app.services import auth_service
from app.schemas import prototype_schema
from app.utils.api_response import api_response
from app.controllers import prototype_controller


# # --- ROUTER ---
# router = APIRouter(
#     prefix="/prototypes",
#     tags=["Prototypes"],
#     dependencies=[Depends(auth_service.require_role(["Admin"]))]
# )


# # --- ROUTES ---
# # Lấy tất cả prototypes
# @router.get("/")
# async def get_prototypes():
#     try:
#         prototypes = await prototype_controller.get_prototypes()
#         return api_response(
#             status_code=200,
#             message="Lấy tất cả prototypes thành công.",
#             details=prototypes
#         )
#     except Exception as e:
#         return api_response(
#             status_code=500,
#             message="Lỗi máy chủ",
#             details=str(e)
#         )


# # Lấy prototype theo ID
# @router.get("/{prototype_id}")
# async def get_prototype(prototype_id: str):
#     try:
#         prototype = await prototype_controller.get_prototype_by_id(prototype_id)
#         return api_response(
#             status_code=200,
#             message="Lấy prototype thành công.",
#             details=prototype
#         )
#     except ValueError as e:
#         return api_response(
#             status_code=404,
#             message="Không tìm thấy prototype.",
#             details=str(e)
#         )
#     except Exception as e:
#         return api_response(
#             status_code=500,
#             message="Lỗi máy chủ.",
#             details=str(e)
#         )


# # Tạo prototype mới
# @router.post("/")
# async def create_prototype(data: prototype_schema.PrototypeCreate):
#     try:
#         data = jsonable_encoder(data)
#         created_prototype = await prototype_controller.create_prototype(data)
#         return api_response(
#             status_code=200,
#             message="Tạo prototype thành công.",
#             details=created_prototype
#         )
#     except Exception as e:
#         return api_response(
#             status_code=500,
#             message="Lỗi máy chủ.",
#             details=str(e)
#         )
      
        
# # Phân cụm embeddings câu hỏi thành prototypes
# @router.post("/cluster")
# async def cluster_question_embeddings():
#     try:
#         await prototype_controller.cluster_question_embeddings()
#         return api_response(
#             status_code=200,
#             message="Phân cụm embeddings câu hỏi thành prototypes thành công.",
#             details=None
#         )
#     except Exception as e:
#         return api_response(
#             status_code=500,
#             message="Lỗi máy chủ.",
#             details=str(e)
#         )


# # Đặt lại (Xóa) toàn bộ prototypes
# @router.delete("/")
# async def reset_prototypes_collection():
#     try:
#         await prototype_controller.reset_prototypes_collection()
#         return api_response(
#             status_code=200,
#             message="Đặt lại collection prototypes thành công.",
#             details=None
#         )
#     except Exception as e:
#         return api_response(
#             status_code=500,
#             message="Lỗi máy chủ.",
#             details=str(e)
#         )