from fastapi import UploadFile

from app.services import question_embedding_service, prototype_service


# # Lấy tất cả embeddings câu hỏi
# async def get_question_embeddings():
#     question_embeddings = await question_embedding_service.get_question_embeddings()
#     return question_embeddings


# # Lấy embedding câu hỏi theo ID
# async def get_question_embedding_by_id(embedding_id: str):
#     question_embedding = await question_embedding_service.get_question_embedding_by_id(embedding_id)
#     return question_embedding


# # Nhập embeddings câu hỏi từ file JSON
# async def import_question_embeddings_file(file: UploadFile):
#     result = await question_embedding_service.import_question_embeddings_file(file=file)
#     await prototype_service.cluster_question_embeddings()
#     return result


# # Tạo embedding câu hỏi mới
# async def create_question_embedding(embedding_data: dict):
#     question_embedding = await question_embedding_service.create_question_embedding(embedding_data)
#     return question_embedding


# # Xóa embedding câu hỏi theo ID
# async def delete_question_embedding(embedding_id: str):
#     deleted = await question_embedding_service.delete_question_embedding(embedding_id)
#     return deleted


# # Đặt lại collection embeddings câu hỏi
# async def reset_question_embeddings_collection():
#     result = await question_embedding_service.reset_question_embeddings_collection()
#     return result