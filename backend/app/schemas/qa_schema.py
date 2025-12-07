from bson import ObjectId
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


# Question Schema
class QuestionSchema(BaseModel):
    question: str
    class Config:
        from_attributes = True
        extra = "forbid"
