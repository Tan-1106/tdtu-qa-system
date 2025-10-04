from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from app.utils.api_response import success_response, error_response

from app.database.crud import question_embedding
from app.schemas.question_embedding import QuestionEmbeddingCreate, QuestionEmbeddingFeedbackUpdate


router = APIRouter(prefix="/question-embeddings", tags=["Question Embeddings"])

# Just for testing, logic is not implemented yet
# Get all question embeddings
@router.get("/")
async def get_question_embeddings():
    try:
        embeddings = await question_embedding.get_question_embeddings()
        return success_response(
            message="Question embeddings retrieved successfully.",
            status_code=200,
            data=embeddings
        )
    except Exception as e:
        return error_response(
            message=str(e),
            status_code=500
        )
        
# Create a new question embedding
@router.post("/")
async def create_question_embedding(question_embedding_data: QuestionEmbeddingCreate):
    try:
        created_question_embedding = await question_embedding.create_question_embedding(question_embedding_data)
        return success_response(
            data=created_question_embedding,
            message="Question embedding created successfully.",
            status_code=201
        )
    except Exception as e:
        return error_response(message=str(e))