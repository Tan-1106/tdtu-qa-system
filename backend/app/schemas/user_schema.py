from bson import ObjectId
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

# Update User Information Schema
class UserInformationUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, description="Full name of the user")
    email: Optional[EmailStr] = Field(default=None, description="Email address of the user")
    
    class Config:
        from_attributes = True
        extra = "forbid"
        
# User Response Schema
class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    full_name: str
    email: EmailStr
    password: str
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = { ObjectId: str }