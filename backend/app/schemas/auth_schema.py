from datetime import datetime
from pydantic import BaseModel
from pydantic import Field, EmailStr

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Type of the token, typically 'bearer'")
    
class TokenData(BaseModel):
    full_name: str | None = Field(None, description="The full name extracted from the token")
    email: EmailStr | None = Field(None, description="The email extracted from the token")
    role: str | None = Field(None, description="The role of the user extracted from the token")
    exp: datetime | None = Field(None, description="Expiration time of the token in UNIX timestamp")

class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=4, max_length=50, description="The full name of the new user")
    email: EmailStr = Field(..., description="The email of the new user")
    password: str = Field(..., min_length=6, max_length=25, description="The password of the new user")
    
    class Config:
        extra = "forbid"

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="The email of the user")
    password: str = Field(..., description="The password of the user")
    
    class Config:
        extra = "forbid"