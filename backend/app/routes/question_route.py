from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app.services import auth_service
from app.schemas import question_schema
from app.controllers import question_controller
from app.utils.api_response import api_response

admin_router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
    dependencies=[Depends(auth_service.require_role(["Admin"]))]
)

user_router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
    dependencies=[Depends(auth_service.get_current_user)]
)


# ADMIN ROUTES
# Get all questions
@admin_router.get("/")
async def get_questions():
    try:
        questions = await question_controller.get_questions()
        return api_response(
            status_code=200,
            details=questions,
            message="Questions retrieved successfully."
        )
    except Exception as e:
        return api_response(
            status_code=500,
            message=str(e)
        )
       
        
# Get a question by ID
@admin_router.get("/{question_id}")
async def get_question(question_id: str):
    try:
        question = await question_controller.get_question_by_id(question_id)
        return api_response(
            status_code=200,
            details=question,
            message="Question retrieved successfully."
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
       
       
# USER ROUTES 
# Ask a question
@user_router.post("/query")
async def query(question: question_schema.QuestionCreate, current_user = Depends(auth_service.get_current_user)):
    try:
        question = jsonable_encoder(question)
        current_user = jsonable_encoder(current_user)
        user_id = current_user["_id"]

        created_question = await question_controller.query(question, user_id)
        return api_response(
            status_code=201,
            details=created_question,
            message="Question asked successfully."
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
      
        
# Leave feedback on an answer
@user_router.post("/{question_id}/feedback")
async def leave_feedback(
    question_id: str,
    feedback: question_schema.LeaveFeedback,
    current_user = Depends(auth_service.get_current_user)
):
    try:
        current_user = jsonable_encoder(current_user)
        feedback = jsonable_encoder(feedback)
        user_id = current_user["_id"]
        feedback_value = feedback["feedback"]

        updated_question = await question_controller.leave_feedback(
            question_id=question_id,
            user_id=user_id,
            feedback=feedback_value
        )
        return api_response(
            status_code=200,
            details=updated_question,
            message="Feedback submitted successfully."
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