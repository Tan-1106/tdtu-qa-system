from fastapi import APIRouter, Depends

from app.services import auth_service
from app.utils.api_response import api_response
from app.schemas import question_embedding_schema
from app.controllers import question_embedding_controller

router = APIRouter(
    prefix="/question-embeddings",
    tags=["Question Embeddings"],
    dependencies=[Depends(auth_service.require_role(["Admin"]))]
)

# Get all question embeddings
@router.get("/")
async def get_question_embeddings():
    try:
        embeddings = await question_embedding_controller.get_question_embeddings()
        return api_response(
            status_code=200,
            details=embeddings,
            message="Question embeddings retrieved successfully."
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )

# Get a question embedding by ID
@router.get("/{embedding_id}")
async def get_question_embedding(embedding_id: str):
    try:
        embedding = await question_embedding_controller.get_question_embedding_by_id(embedding_id)
        return api_response(
                status_code=200,
                details=embedding,
                message="Question embedding retrieved successfully."
            )
    except ValueError as e:
        return api_response(
            status_code=404,
            message=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )

# Create a new question embedding
@router.post("/")
async def create_question_embedding(data: question_embedding_schema.QuestionEmbeddingCreate):
    try:
        created_question_embedding = await question_embedding_controller.create_question_embedding(data)
        return api_response(
            status_code=201,
            message="Question embedding created successfully.",
            details=created_question_embedding
        )
    except ValueError as e:
        return api_response(
            status_code=400,
            message=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )
    
# Delete a question embedding by ID
@router.delete("/{embedding_id}")
async def delete_question_embedding(embedding_id: str):
    try:
        await question_embedding_controller.delete_question_embedding(embedding_id)
        return api_response(
            status_code=200,
            message="Question embedding deleted successfully."
        )
    except ValueError as e:
        return api_response(
            status_code=404,
            message=str(e)
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )
    
# Reset (Delete) question embeddings collection
@router.delete("/")
async def reset_question_embeddings_collection():
    try:
        await question_embedding_controller.reset_question_embeddings_collection()
        return api_response(
            status_code=200,
            message="All question embeddings deleted successfully."
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )
        