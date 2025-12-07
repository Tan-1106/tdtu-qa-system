from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from pydantic import Field, EmailStr


# ELIT Login Schema
class ELITLoginCode(BaseModel):
    code: str = Field(..., description="The authorization code received from ELIT after user login")
    class Config:
        extra = "forbid"
        

# ELIT Login Response Schema
class ELITLoginResponse(BaseModel):
    sub: str = Field(..., description="Student ID associated with the user")
    name: str = Field(..., description="Full name of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    image: Optional[str] = Field(None, description="URL of the user's profile image")
    is_admin: bool = Field(False, description="Indicates if the user has admin privileges")
    is_teacher: bool = Field(False, description="Indicates if the user is a teacher")
    is_student: bool = Field(True, description="Indicates if the user is a student")
    faculty: Optional[str] = Field(None, description="Faculty name of the user")
    faculty_code: Optional[str] = Field(None, description="Faculty code of the user")
    is_faculty_manager: bool = Field(False, description="Indicates if the user is a faculty manager")
    class Config:
        extra = "ignore"


# Token Record Schema
class TokensRecord(BaseModel):
    sub: str = Field(..., description="ID of the user associated with the tokens")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    revoked: bool = Field(False, description="Indicates if the refresh token has been revoked")
    created_at: datetime = Field(..., description="Timestamp when the tokens were created")
    revoked_at: Optional[datetime] = Field(None, description="Timestamp when the refresh token was revoked, if applicable")
    class Config:
        from_attributes = True
        extra = "ignore"
        
    
# Refresh Token Schema
class RefreshTokensRequest(BaseModel):
    refresh_token: str = Field(..., description="JWT refresh token")
    class Config:
        extra = "forbid"