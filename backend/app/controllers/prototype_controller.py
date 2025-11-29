from app.services import prototype_service


# # Lấy tất cả prototypes
# async def get_prototypes():
#     prototypes = await prototype_service.get_prototypes()
#     return prototypes


# # Lấy prototype theo ID
# async def get_prototype_by_id(prototype_id: str):
#     prototype = await prototype_service.get_prototype_by_id(prototype_id)
#     return prototype


# # Tạo prototype
# async def create_prototype(prototype_data: dict):
#     prototype = await prototype_service.create_prototype(prototype_data)
#     return prototype


# # Phân cụm embeddings câu hỏi thành prototypes
# async def cluster_question_embeddings():
#     response = await prototype_service.cluster_question_embeddings()
#     return response


# # Đặt lại collection prototypes
# async def reset_prototypes_collection():
#     result = await prototype_service.reset_prototypes_collection()
#     return result
