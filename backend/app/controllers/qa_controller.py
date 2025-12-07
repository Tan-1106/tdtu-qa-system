from langdetect import detect
from fastapi.encoders import jsonable_encoder

from app.services import qa_service
from app.schemas.qa_schema import Feedback
from app.utils.basic_information import Role
from app.utils.api_response import UserError


# Question-Answering
async def get_answer(question: str, current_user: dict):
    question_language = detect(question)
    
    question_record = jsonable_encoder(await qa_service.create_question_record(
        question=question,
        user_id=current_user["_id"],
        user_sub=current_user["sub"],
        user_faculty=current_user["faculty"]
    ))
    
    user_faculty = current_user["faculty"] if current_user["faculty"] is not None else ""
    if question_language == "vi":
        answer = await qa_service.get_answer(question, user_faculty, "vi")
    else:
        question_in_vietnamese = await qa_service.translate_to_vietnamese(question)
        answer = await qa_service.get_answer(question_in_vietnamese, user_faculty, "en")
        
    question_record = await qa_service.update_question_record_with_answer(question_record["_id"], answer)
        
    return answer


# Leave feedback for a question
async def leave_feedback(qa_record_id: str, feedback: str, current_user: dict):
    qa_record = jsonable_encoder(await qa_service.get_qa_record_by_id(qa_record_id))
    if qa_record["user_id"] != current_user["_id"]:
        raise UserError("You are not authorized to leave feedback for this question record.")
    
    if feedback not in [f.value for f in Feedback]:
        raise UserError("Invalid feedback value.")
    
    success = await qa_service.leave_feedback_for_question(qa_record_id, feedback, current_user["_id"])
    return success


# Get current user's question records
async def get_user_question_records(
    page: int,
    limit: int,
    feedback: str,
    has_manager_answer: bool,
    current_user: dict
):
    if current_user["role"] == Role.ADMIN.value or current_user["is_faculty_manager"]:
        raise UserError("Only regular users can access their question records.")
    
    records = await qa_service.get_question_records_by_user_id(
        page, limit,
        feedback,
        has_manager_answer,
        current_user["_id"]
    )
    return records