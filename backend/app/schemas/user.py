from bson import ObjectId
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

# Create User Schema
class UserCreate(BaseModel):
    full_name: str = Field(..., description="Full name of the user")
    email: str = Field(..., description="Email address of the user")
    password: str = Field(..., description="Password of the user")
    
    class Config:
        orm_mode = True
        extra = "forbid"

# Update User Information Schema
class UserInformationUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, description="Full name of the user")
    email: Optional[str] = Field(default=None, description="Email address of the user")
    
    class Config:
        orm_mode = True
        extra = "forbid"
        
# Update User Password Schema
class UserPasswordUpdate(BaseModel):
    old_password: str = Field(..., description="Old password of the user")
    new_password: str = Field(..., description="New password of the user")
    
    class Config:
        orm_mode = True
        extra = "forbid" 
        
# User Response Schema
class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    full_name: str
    email: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        populate_by_name = True
        json_encoders = { ObjectId: str }