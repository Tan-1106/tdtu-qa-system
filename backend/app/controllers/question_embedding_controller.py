from fastapi.encoders import jsonable_encoder
from app.schemas import question_embedding_schema
from app.services import question_embedding_service

# Get all question embeddings
async def get_question_embeddings():
    response = await question_embedding_service.get_question_embeddings()
    return response

# Get a question embedding by ID
async def get_question_embedding_by_id(embedding_id: str):
    response = await question_embedding_service.get_question_embedding_by_id(embedding_id)
    return response

# Create a new question embedding
async def create_question_embedding(embedding_data: question_embedding_schema.QuestionEmbeddingCreate):
    embedding_data = jsonable_encoder(embedding_data)
    response = await question_embedding_service.create_question_embedding(embedding_data)
    return response

# Update feedback for a question embedding
async def update_question_embedding_feedback(embedding_id: str, feedback: question_embedding_schema.QuestionEmbeddingFeedbackUpdate):
    feedback = jsonable_encoder(feedback)
    response = await question_embedding_service.update_question_embedding_feedback(embedding_id, feedback['feedback_score'])
    return response

# Delete a question embedding by ID
async def delete_question_embedding(embedding_id: str):
    response = await question_embedding_service.delete_question_embedding(embedding_id)
    return response

# Reset (Delete) question embeddings collection
async def reset_question_embeddings_collection():
    response = await question_embedding_service.reset_question_embeddings_collection()
    return response