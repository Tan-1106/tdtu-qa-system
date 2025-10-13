from typing import List
from bson import ObjectId
from pydantic import BaseModel, Field

class QuestionEmbeddingMetadata(BaseModel):
    doc_id: str = Field(..., description="ID of the associated document")
    chunk_index: int = Field(..., description="Index of the chunk in the document")
    feedback_score: int = Field(default=0, description="Feedback score: +1 like, -1 dislike")
    feedback_count: int = Field(default=0, description="Number of feedback for this question")
    
    class Config:
        from_attributes = True
        extra = "forbid"

# Create Document Schema
class QuestionEmbeddingCreate(BaseModel):
    vector: List[float] = Field(..., description="The embedding vector")
    metadata: QuestionEmbeddingMetadata = Field(..., description="Metadata associated with the question embedding")

    class Config:
        from_attributes = True
        extra = "forbid"
        
# Feedback Update Schema
class QuestionEmbeddingFeedbackUpdate(BaseModel):
    feedback_score: int = Field(..., description="Feedback score: +1 like, -1 dislike")
    
    class Config:
        extra = "forbid"
        
# Question Embedding Response Schema
class QuestionEmbeddingResponse(BaseModel):
    id: str
    vector: List[float]
    metadata: QuestionEmbeddingMetadata

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = { ObjectId: str }