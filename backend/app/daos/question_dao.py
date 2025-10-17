from bson import ObjectId
from datetime import datetime, timezone

from app.databases import mongo
from app.utils import serializer
from app.schemas import question_schema

# Read all questions
async def get_questions() -> list[question_schema.QuestionResponse]:
    questions = []
    async for question in mongo.get_questions_collection().find():
        questions.append(question_schema.QuestionResponse(**serializer.question_serialize(question)))
    return questions

# Read a question by ID
async def get_question_by_id(question_id: str) -> question_schema.QuestionResponse:
    question = await mongo.get_questions_collection().find_one({"_id": ObjectId(question_id)})
    if not question:
        raise ValueError("Question not found")
    return question_schema.QuestionResponse(**serializer.question_serialize(question))

# Create a new question
async def create_question(question: dict) -> question_schema.QuestionResponse:
    question["created_at"] = datetime.now(timezone.utc)
    question["status"] = "Pending"
    
    result = await mongo.get_questions_collection().insert_one(question)
    
    created_question = await mongo.get_questions_collection().find_one({"_id": result.inserted_id})
    return question_schema.QuestionResponse(**serializer.question_serialize(created_question))

