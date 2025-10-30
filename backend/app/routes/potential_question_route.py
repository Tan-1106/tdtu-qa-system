from fastapi import APIRouter, Depends

from app.services import auth_service
from app.utils.api_response import api_response
from app.schemas import potential_question_schema
from app.controllers import potential_question_controller

route = APIRouter(
    prefix="/potential-questions",
    tags=["Potential Questions"],
    dependencies=[Depends(auth_service.require_role(["Admin"]))]
)

# Get all potential questions
@route.get("/")
async def get_potential_questions():
    try:
        potential_questions = await potential_question_controller.get_potential_questions()
        return api_response(
            status_code=200,
            message="Potential questions retrieved successfully.",
            details=potential_questions
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )

# Get potential questions by doc_id & chunk_index
@route.get("/{doc_id}/chunks/{chunk_index}")
async def get_potential_questions_by_chunk(doc_id: str, chunk_index: int):
    try:
        potential_questions = await potential_question_controller.get_potential_questions_by_chunk(doc_id, chunk_index)
        return api_response(
            status_code=200,
            message="Potential questions retrieved successfully.",
            details=potential_questions
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )

# Create a potential question for chunk
@route.post("/{doc_id}/chunks/{chunk_index}")
async def add_potential_question(doc_id: str, chunk_index: int, potential_question_data: potential_question_schema.AddPotentialQuestion):
    try:
        print("LOG: ROUTE - CREATE POTENTIAL QUESTION")
        created_questions = await potential_question_controller.add_potential_question(doc_id, chunk_index, potential_question_data)
        return api_response(
            status_code=201,
            message="Potential question created successfully.",
            details=created_questions
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

# Update a potential question of a chunk
@route.put("/{doc_id}/chunks/{chunk_index}/questions/{question_index}")
async def update_potential_question(doc_id: str, chunk_index: int, question_index: int, question_update: potential_question_schema.PotentialQuestionUpdate):
    try:
        print("LOG: ROUTE")
        updated_question = await potential_question_controller.update_potential_question(doc_id, chunk_index, question_index, question_update)
        return api_response(
            status_code=200,
            message="Potential question updated successfully.",
            details=updated_question
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )

# Delete a potential question of a chunk
@route.delete("/{doc_id}/chunks/{chunk_index}/questions/{question_index}")
async def delete_potential_question(doc_id: str, chunk_index: int, question_index: int):
    try:
        deleted = await potential_question_controller.delete_potential_question(doc_id, chunk_index, question_index)
        return api_response(
            status_code=200,
            message="Potential question deleted successfully.",
            details=deleted
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )