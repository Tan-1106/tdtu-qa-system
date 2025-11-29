from typing import List
from datetime import datetime, timezone
from fastapi.encoders import jsonable_encoder

from app.databases import mongo
from app.utils import serializer
from app.schemas import potential_question_schema


# # Tạo các câu hỏi tiềm năng cho một đoạn văn bản
# async def create_potential_questions(potential_question_data: potential_question_schema.PotentialQuestionCreate) -> potential_question_schema.PotentialQuestionResponse:
#     potential_question_data = jsonable_encoder(potential_question_data)
#     potential_question_data["created_at"] = datetime.now(timezone.utc)
#     result = await mongo.get_potential_questions_collection().insert_one(potential_question_data)
#     created_pq = await mongo.get_potential_questions_collection().find_one({"_id": result.inserted_id})
#     return potential_question_schema.PotentialQuestionResponse(**serializer.potential_question_serialize(created_pq))


# # Lấy tất cả các câu hỏi tiềm năng
# async def get_potential_questions() -> List[potential_question_schema.PotentialQuestionResponse]:
#     pq_list = []
#     async for pq in mongo.get_potential_questions_collection().find({}):
#         pq_list.append(potential_question_schema.PotentialQuestionResponse(**serializer.potential_question_serialize(pq)))
#     return pq_list


# # Lấy các câu hỏi tiềm năng theo doc_id và chunk_index
# async def get_potential_questions_by_chunk(doc_id: str, chunk_index: int) -> potential_question_schema.PotentialQuestionResponse:
#     query = {"doc_id": doc_id, "chunk_index": chunk_index}
#     async for pq in mongo.get_potential_questions_collection().find(query):
#         return potential_question_schema.PotentialQuestionResponse(**serializer.potential_question_serialize(pq))
#     raise ValueError("Không tìm thấy câu hỏi tiềm năng cho đoạn văn bản được chỉ định.")

# # Thêm một câu hỏi tiềm năng cho một đoạn văn bản
# async def add_potential_question(question_data: dict) -> potential_question_schema.PotentialQuestionResponse:
#     query = {"doc_id": question_data["doc_id"], "chunk_index": question_data["chunk_index"]}
#     pq = await mongo.get_potential_questions_collection().find_one(query)
    
#     if pq:
#         potential_questions = pq.get("potential_questions", [])
#         potential_questions.append(question_data["question"])
        
#         embedding_ids = pq.get("embedding_ids", [])
#         embedding_ids.append(question_data["embedding_id"])
        
#         update_data = {
#             "potential_questions": potential_questions,
#             "embedding_ids": embedding_ids,
#             "updated_at": datetime.now(timezone.utc)
#         }
        
#         await mongo.get_potential_questions_collection().update_one(query, {"$set": update_data})
        
#         updated_pq = await mongo.get_potential_questions_collection().find_one(query)
#         return potential_question_schema.PotentialQuestionResponse(**serializer.potential_question_serialize(updated_pq))
#     else:
#         raise ValueError("Không tìm thấy đoạn văn bản. Không thể thêm câu hỏi tiềm năng.")


# # Cập nhật một câu hỏi tiềm năng của một đoạn văn bản
# async def update_potential_question(doc_id: str, chunk_index: int, question_index: int, new_question: str) -> potential_question_schema.PotentialQuestionResponse:
#     query = {"doc_id": doc_id, "chunk_index": chunk_index}
#     pq = await mongo.get_potential_questions_collection().find_one(query)
#     if not pq:
#         raise Exception("Không tìm thấy câu hỏi tiềm năng.")
    
#     potential_questions = pq.get("potential_questions", [])
#     if question_index < 0 or question_index >= len(potential_questions):
#         raise Exception("Chỉ số câu hỏi không hợp lệ.")
    
#     potential_questions[question_index] = new_question
    
#     update_data = {
#         "potential_questions": potential_questions,
#         "updated_at": datetime.now(timezone.utc)
#     }
    
#     await mongo.get_potential_questions_collection().update_one(query, {"$set": update_data})
    
#     updated_pq = await mongo.get_potential_questions_collection().find_one(query)
#     return potential_question_schema.PotentialQuestionResponse(**serializer.potential_question_serialize(updated_pq))


# # Xóa một câu hỏi tiềm năng của một đoạn văn bản
# async def delete_potential_question(doc_id: str, chunk_index: int, question_index: int) -> dict:
#     query = {"doc_id": doc_id, "chunk_index": chunk_index}
#     pq = await mongo.get_potential_questions_collection().find_one(query)
#     if not pq:
#         raise Exception("Không tìm thấy câu hỏi tiềm năng.")
    
#     potential_questions = pq.get("potential_questions", [])
#     if question_index < 0 or question_index >= len(potential_questions):
#         raise Exception("Chỉ số câu hỏi không hợp lệ.")
    
#     deleted_question = potential_questions.pop(question_index)
    
#     potential_question_embedding_ids = pq.get("embedding_ids", [])
#     if question_index < len(potential_question_embedding_ids):
#         potential_question_embedding_ids.pop(question_index)
    
#     update_data = {
#         "potential_questions": potential_questions,
#         "embedding_ids": potential_question_embedding_ids,
#         "updated_at": datetime.now(timezone.utc)
#     }
    
#     await mongo.get_potential_questions_collection().update_one(query, {"$set": update_data})
    
#     return {"deleted_question": deleted_question}


# # Xóa các câu hỏi tiềm năng theo doc_id
# async def delete_potential_questions_by_doc_id(doc_id: str) -> dict:
#     result = await mongo.get_potential_questions_collection().delete_many({"doc_id": doc_id})
#     return {"deleted_count": result.deleted_count}