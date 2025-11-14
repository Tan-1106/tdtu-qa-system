import asyncio
from fastapi.encoders import jsonable_encoder

from app.daos import potential_question_dao
from app.services import model_service, question_embedding_service, prototype_service

# Get all potential questions
async def get_potential_questions():
    potential_questions = await potential_question_dao.get_potential_questions()
    return potential_questions


# Get potential questions by doc_id and chunk_index
async def get_potential_questions_by_chunk(doc_id: str, chunk_index: int):
    potential_questions = await potential_question_dao.get_potential_questions_by_chunk(doc_id, chunk_index)
    return potential_questions


# Add a potential question for a chunk
async def add_potential_question(question_data: dict):
    # Add embedding for the new potential question
    question = question_data["question"]
    
    # Wrap blocking I/O in executor
    loop = asyncio.get_event_loop()
    embedding = await loop.run_in_executor(
        None,
        lambda: model_service.get_embedding(question)
    )
    qe = {
        "vector": embedding,
        "metadata": { "doc_id": question_data["doc_id"], "chunk_index": question_data["chunk_index"] }
    }
    embedding_record = await question_embedding_service.create_question_embedding(qe)
    embedding_record = jsonable_encoder(embedding_record)
    embedding_id = embedding_record["id"]

    # Cluster question embeddings after adding new one
    await prototype_service.cluster_question_embeddings()

    # Associate the embedding ID with the potential question
    question_data["embedding_id"] = embedding_id
    
    # Create the potential question record
    created_question = await potential_question_dao.add_potential_question(question_data)
    return created_question


# Update a potential question of a chunk
async def update_potential_question(doc_id: str, chunk_index: int, question_index: int, new_question: str):
    updated_question = await potential_question_dao.update_potential_question(doc_id, chunk_index, question_index, new_question)
    updated_question = jsonable_encoder(updated_question)
    new_question = updated_question["potential_questions"][question_index]
    
    # Wrap blocking I/O in executor
    loop = asyncio.get_event_loop()
    updated_question_embedding = await loop.run_in_executor(
        None,
        lambda: model_service.get_embedding(new_question)
    )
    
    await question_embedding_service.update_question_embedding(
        embedding_id=updated_question['embedding_ids'][question_index],
        embedding_update={
            "vector": updated_question_embedding,
            "metadata": { "doc_id": doc_id, "chunk_index": chunk_index }
        }
    )
    
    await prototype_service.cluster_question_embeddings()
    
    return updated_question


# Delete a potential question of a chunk
async def delete_potential_question(doc_id: str, chunk_index: int, question_index: int):
    potential_questions = await potential_question_dao.get_potential_questions_by_chunk(doc_id, chunk_index)
    potential_questions = jsonable_encoder(potential_questions)
    print("Potential questions fetched for deletion:", potential_questions)
    
    if not potential_questions:
        raise Exception("Potential question not found.")
    deleted_question = await potential_question_dao.delete_potential_question(doc_id, chunk_index, question_index)
    print("Deleted potential question:", deleted_question)
    
    embedding_id_to_delete = potential_questions["embedding_ids"][question_index]
    result = await question_embedding_service.delete_question_embedding(embedding_id_to_delete)
    await prototype_service.cluster_question_embeddings()
    
    if not result:
        raise Exception("Failed to delete associated question embedding.")
    
    return deleted_question


# Delete potential questions by doc_id
async def delete_potential_questions_by_doc_id(doc_id: str):
    result = await potential_question_dao.delete_potential_questions_by_doc_id(doc_id)
    return result