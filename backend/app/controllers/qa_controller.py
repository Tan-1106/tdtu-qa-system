from langdetect import detect

from app.services import qa_service


# Question-Answering
async def get_answer(question: str, current_user: dict):
    question_language = detect(question)
    
    question_record = await qa_service.create_question_record(
        question=question,
        user_id=current_user["_id"],
        user_role=current_user["role"],
        user_faculty=current_user["faculty"]
    )