from fastapi.encoders import jsonable_encoder

from app.schemas import question_schema
from app.services import question_service

# Get all questions
async def get_questions():
    questions = await question_service.get_questions()
    return questions

# Get a question by ID
async def get_question_by_id(question_id: str):
    question = await question_service.get_question_by_id(question_id)
    return question

# Create a new question
async def create_question(question_data: question_schema.QuestionCreate, user_id: str):
    question_data = jsonable_encoder(question_data)
    question_data['user_id'] = user_id
    
    question = await question_service.create_question(question_data)
    return question

# Ask a question
async def query(question_data: question_schema.QuestionCreate, user_id: str):
    question_data = jsonable_encoder(question_data)
    question_data['user_id'] = user_id
    
    # Create the question
    question = await question_service.create_question(question_data)
    try:
        # Get the answer
        answer = await question_service.query(question_data)
        # Update question status with answer
        result = await question_service.update_question_status(question.id, answer)

    except Exception as e:
        await question_service.update_question_status(question.id, f"Error: Cannot get answer. {str(e)}", status="Failed")
        raise e

    return result

# Leave feedback for a question
async def leave_feedback(question_id: str, user_id: str, feedback: int):
    question = await question_service.leave_feedback(question_id, user_id, feedback)
    return question