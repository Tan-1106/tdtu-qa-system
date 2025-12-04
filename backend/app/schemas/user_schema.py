from bson import ObjectId
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


# User Creation Schema
class UserRecord(BaseModel):
    id: str = Field(alias="_id")
    sub: str
    name: str
    email: EmailStr
    image: Optional[str] = None
    role: str
    faculty: str
    banned: bool
    created_at: datetime
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = { ObjectId: str }
        
        
# Assign Faculty Manager Schema
class AssignFacultySchema(BaseModel):
    faculty: str
    class Config:
        from_attributes = True
        extra = "forbid"