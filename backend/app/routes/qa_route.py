from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder

from app.schemas import qa_schema
from app.services import auth_service
from app.controllers import qa_controller
from app.utils.api_response import api_response


# --- ROUTER ---
router = APIRouter(
    prefix="/qa",
    tags=["Q&A"],
    dependencies=[Depends(auth_service.get_current_user)]
)


# --- ROUTES ---
# Question-Answering
@router.post("/ask")
async def qa(
    data: qa_schema.QuestionSchema,
    current_user = Depends(auth_service.get_current_user)
):
    data = jsonable_encoder(data)
    current_user = jsonable_encoder(current_user)
    answer = await qa_controller.get_answer(data["question"], current_user)
    return api_response(
        status_code=200,
        message="Get answer successfully.",
        details=answer
)
    
    
# Leave feedback for a question
@router.post("/feedback/{qa_record_id}")
async def leave_feedback(
    qa_record_id: str,
    data: qa_schema.FeedbackSchema,
    current_user = Depends(auth_service.get_current_user)
):
    data = jsonable_encoder(data)
    current_user = jsonable_encoder(current_user)
    success = await qa_controller.leave_feedback(qa_record_id, data["feedback"], current_user)
    return api_response(
        status_code=200,
        message="Leave feedback successfully.",
        details=success
    )
    
    
# Get current user's question records
@router.get("/history")
async def get_user_question_records(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    feedback: str = Query(None),
    has_manager_answer: bool = Query(None),
    current_user = Depends(auth_service.get_current_user)
):
    current_user = jsonable_encoder(current_user)
    records = await qa_controller.get_user_question_records(page, limit, feedback, has_manager_answer, current_user)
    return api_response(
        status_code=200,
        message="Get question records successfully.",
        details=records
    )