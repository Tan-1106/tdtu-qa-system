from app.daos import question_embedding_dao

# Get all question embeddings
async def get_question_embeddings():
    question_embeddings = await question_embedding_dao.get_question_embeddings()
    return question_embeddings

# Get a question embedding by ID
async def get_question_embedding_by_id(embedding_id: str):
    question_embedding = await question_embedding_dao.get_question_embedding_by_id(embedding_id)
    return question_embedding

# Create a new question embedding
async def create_question_embedding(embedding: dict):
    created_embedding = await question_embedding_dao.create_question_embedding(embedding)
    return created_embedding

# Update feedback for a question embedding
async def update_question_embedding_feedback(embedding_id: str, score: int):
    updated_embedding = await question_embedding_dao.update_question_embedding_feedback(embedding_id, score)
    return updated_embedding

# Delete a question embedding by ID
async def delete_question_embedding(embedding_id: str):
    deleted = await question_embedding_dao.delete_question_embedding(embedding_id)
    return deleted

# Reset (Delete) question embeddings collection
async def reset_question_embeddings_collection():
    deleted = await question_embedding_dao.reset_question_embeddings_collection()
    return deleted