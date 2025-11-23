import asyncio
from typing import List

from app.services import model_service
from app.daos import question_embedding_dao, potential_question_dao, prototype_dao


# Lấy tất cả các embedding của câu hỏi tiềm năng
async def get_question_embeddings():
    question_embeddings = await question_embedding_dao.get_question_embeddings()
    return question_embeddings


# Lấy một embedding của câu hỏi theo ID
async def get_question_embedding_by_id(embedding_id: str):
    question_embedding = await question_embedding_dao.get_question_embedding_by_id(embedding_id)
    return question_embedding


# Tạo một embedding của câu hỏi mới
async def create_question_embedding(embedding: dict):
    created_embedding = await question_embedding_dao.create_question_embedding(embedding)
    return created_embedding


# Nhập file các embedding của câu hỏi
async def import_question_embeddings_file(file):
    result = await question_embedding_dao.import_question_embeddings_file(file=file)
    return result


# Cập nhật một embedding của câu hỏi theo ID
async def update_question_embedding(embedding_id: str, embedding_update: dict):
    updated_embedding = await question_embedding_dao.update_question_embedding(embedding_id, embedding_update)
    return updated_embedding


# Xóa một embedding của câu hỏi theo ID
async def delete_question_embedding(embedding_id: str):
    deleted = await question_embedding_dao.delete_question_embedding(embedding_id)
    return deleted


# Xóa các embedding của câu hỏi theo document ID
async def delete_question_embeddings_by_doc_id(doc_id: str):
    deleted = await question_embedding_dao.delete_question_embeddings_by_doc_id(doc_id)
    return deleted


# Đặt lại collection embeddings của câu hỏi tiềm năng
async def reset_question_embeddings_collection():
    deleted_question_embeddings = await question_embedding_dao.reset_question_embeddings_collection()
    deleted_prototypes = await prototype_dao.reset_prototypes_collection()
    
    deleted = deleted_question_embeddings and deleted_prototypes
    return deleted


# Tìm kiếm ngữ nghĩa cho embeddings của câu hỏi tiềm năng
async def semantic_search_question_embeddings(query_vector: List[float], top_k: int, relevant_embedding_ids: List[str] = None):
    question_embeddings = await question_embedding_dao.semantic_search_question_embeddings(query_vector, top_k, relevant_embedding_ids)
    return question_embeddings


# Tạo các câu hỏi tiềm năng cho một đoạn văn bản
async def create_question_embeddings(doc_id: str, chunk_idx: int, chunk: str, num_questions: int = 5, is_appendix: bool = False):
    loop = asyncio.get_event_loop()
    
    if is_appendix:
        generated_questions_list = await loop.run_in_executor(
            None,
            lambda: model_service.create_questions_appendix(chunk, num_questions=num_questions)
        )
    else:
        generated_questions_list = await loop.run_in_executor(
            None,
            lambda: model_service.create_questions(chunk, num_questions=num_questions)
        )

    question_embeddings = []
    async def create_single_embedding(question):
        embedding = await loop.run_in_executor(
            None,
            lambda: model_service.get_embedding(question)
        )
        question_embedding = {
            "vector": embedding,
            "metadata": {"doc_id": doc_id, "chunk_index": chunk_idx}
        }
        qe = await create_question_embedding(question_embedding)
        question_embeddings.append(qe)
    
    await asyncio.gather(*[
        create_single_embedding(q) for q in generated_questions_list
    ])
    
    potential_question = {
        "doc_id": doc_id,
        "chunk_index": chunk_idx,
        "potential_questions": generated_questions_list,
        "embedding_ids": [str(qe.id) for qe in question_embeddings]
    }
    await potential_question_dao.create_potential_questions(potential_question)

    return {
        "doc_id": doc_id,
        "chunk_index": chunk_idx,
        "chunk": chunk,
        "questions_list": generated_questions_list
    }