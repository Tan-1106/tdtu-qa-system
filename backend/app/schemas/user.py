from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timezone

# Schema dùng khi tạo user (request)
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"
    
# Schema dùng khi cập nhật user (request)
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None

# Schema dùng khi trả về user (response)
class UserResponse(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    full_name: str
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        populate_by_name = True