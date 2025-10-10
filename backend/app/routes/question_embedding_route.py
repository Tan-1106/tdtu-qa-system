from fastapi import APIRouter
from app.utils.api_response import api_response
from app.controllers import question_embedding_controller

router = APIRouter(prefix="/question-embeddings", tags=["Question Embeddings"])

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
        if embedding:
            return api_response(
                status_code=200,
                details=embedding,
                message="Question embedding retrieved successfully."
            )
        else:
            return api_response(
                status_code=404,
                message="Question embedding not found."
            )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )

# Create a new question embedding
@router.post("/")
async def create_question_embedding(data: dict):
    try:
        created_question_embedding = await question_embedding_controller.create_question_embedding(data)
        return api_response(
            status_code=201,
            message="Question embedding created successfully.",
            details=created_question_embedding
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )
        
# Update feedback for a question embedding
@router.patch("/{embedding_id}/feedback")
async def update_question_embedding_feedback(embedding_id: str, score: int):
    try:
        updated_embedding = await question_embedding_controller.update_question_embedding_feedback(embedding_id, score)
        if updated_embedding:
            return api_response(
                status_code=200,
                message="Question embedding feedback updated successfully.",
                details=updated_embedding
            )
        else:
            return api_response(
                status_code=404,
                message="Question embedding not found."
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
        success = await question_embedding_controller.delete_question_embedding(embedding_id)
        if success:
            return api_response(
                status_code=200,
                message="Question embedding deleted successfully."
            )
        else:
            return api_response(
                status_code=500,
                message="Failed to delete question embedding."
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
        success = await question_embedding_controller.reset_question_embeddings_collection()
        if success:
            return api_response(
                status_code=200,
                message="All question embeddings deleted successfully."
            )
        else:
            return api_response(
                status_code=500,
                message="Failed to delete all question embeddings."
            )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )