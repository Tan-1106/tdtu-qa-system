from app.services import potential_question_service


# Get all potential questions
async def get_potential_questions():
    potential_questions = await potential_question_service.get_potential_questions()
    return potential_questions


# Get potential questions by doc_id and chunk_index
async def get_potential_questions_by_chunk(doc_id: str, chunk_index: int):
    potential_questions = await potential_question_service.get_potential_questions_by_chunk(doc_id, chunk_index)
    return potential_questions


# Add a potential question for a chunk
async def add_potential_question(doc_id: str, chunk_index: int, question_data: dict):
    question = question_data["question"]
    potential_question_data = {
        "doc_id": doc_id,
        "chunk_index": chunk_index,
        "question": question
    }
    created_questions = await potential_question_service.add_potential_question(potential_question_data)
    return created_questions


# Update a potential question of a chunk
async def update_potential_question(doc_id: str, chunk_index: int, question_index: int, question_update: dict):
    new_question = question_update["new_question"]
    updated_question = await potential_question_service.update_potential_question(doc_id, chunk_index, question_index, new_question)
    return updated_question


# Delete a potential question of a chunk
async def delete_potential_question(doc_id: str, chunk_index: int, question_index: int):
    deleted = await potential_question_service.delete_potential_question(doc_id, chunk_index, question_index)
    return deleted


# Delete potential questions by doc_id
async def delete_potential_questions_by_doc_id(doc_id: str):
    result = await potential_question_service.delete_potential_questions_by_doc_id(doc_id)
    return result