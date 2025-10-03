from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

# Create Popular Question Schema
class PopularQuestionCreate(BaseModel):
    question: str = Field(..., description="The popular question content")
    answer: str = Field(..., description="The answer content")
    source_docs: List[str] = Field(..., description="List of source document IDs")
    ask_count: int = Field(..., description="Number of times the question has been asked")
    
    class Config:
        orm_mode = True
        extra = "forbid"
        
# Update Answer Schema
class PopularQuestionAnswerUpdate(BaseModel):
    answer: str = Field(..., description="The updated answer content")
    source_docs: Optional[List[str]] = Field(default=None, description="Updated list of source document IDs")
    
    class Config:
        orm_mode = True
        extra = "forbid"
        
# Popular Question Response Schema
class PopularQuestionResponse(BaseModel):
    id: str = Field(alias="_id")
    question: str
    answer: str
    source_docs: List[str]
    ask_count: int

    class Config:
        orm_mode = True
        populate_by_name = True
        json_encoders = { ObjectId: str }