from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    full_name: str = Field(...)
    email: EmailStr = Field(...)
    hashed_password: str = Field(...)
    role: str = Field(default="user")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True