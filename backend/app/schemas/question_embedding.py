from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

# Create Document Schema
class QuestionEmbeddingCreate(BaseModel):
    id: str = Field(..., description="ID of the question embedding")
    vector: List[float] = Field(..., description="The embedding vector")
    
    class Metadata(BaseModel):
        doc_id: str = Field(..., description="ID of the associated document")
        chunk_index: int = Field(..., description="Index of the chunk in the document")
        prototype_id: str = Field(..., description="ID of the prototype where this question is clustered")
        feedback_score: int = Field(default=0, description="Feedback score: +1 like, -1 dislike")
        feedback_count: int = Field(default=0, description="Number of feedback for this question")

    metadata: Metadata = Field(..., description="Metadata associated with the question embedding")
    
    class Config:
        orm_mode = True
        extra = "forbid"
        
# Feedback Update Schema
class QuestionEmbeddingFeedbackUpdate(BaseModel):
    feedback_score: int = Field(..., description="Feedback score: +1 like, -1 dislike")
    feedback_count: int = Field(..., description="Number of feedback for this question")
    
    class Config:
        orm_mode = True
        extra = "forbid"
        
# Question Embedding Response Schema
class QuestionEmbeddingResponse(BaseModel):
    id: str = Field(alias="_id")
    vector: List[float]

    class MetadataResponse(BaseModel):
        doc_id: str
        chunk_index: int
        prototype_id: str
        feedback_score: int
        feedback_count: int
        
    metadata: MetadataResponse

    class Config:
        orm_mode = True
        populate_by_name = True
        json_encoders = { ObjectId: str }