from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel, Field

# Create Answer Feedback Schema
class AnswerFeedbackCreate(BaseModel):
    user_id: str = Field(..., description="ID of the user providing feedback")
    question: str = Field(..., description="The question content")
    answer: str = Field(..., description="The answer content")
    feedback: int = Field(..., description="Feedback on the answer (Like/Dislike | 1 for Like, -1 for Dislike)")

    class Config:
        from_attributes = True
        extra = "forbid"
        
# Update Feedback Status Schema
class UpdateFeedbackStatus(BaseModel):
    status: str = Field(..., description="Status of the feedback (e.g., 'Pending', 'Valid', 'Invalid')")
    
    class Config:
        from_attributes = True
        extra = "forbid"

# Answer Feedback Response Schema
class AnswerFeedbackResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    question: str
    answer: str
    feedback: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = { ObjectId: str }