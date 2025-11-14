from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel, Field

# Refresh Token Schema
class RefreshTokenCreate(BaseModel):
    user_id: str = Field(..., description="ID of the user")
    hashed_token: str = Field(..., description="Hashed refresh token")
    
    class Config:
        from_attributes = True
        extra = "forbid"
      
        
# Revoke Refresh Token Schema
class RefreshTokenRevoke(BaseModel):
    token: str = Field(..., description="The refresh token to be revoked")
    
    class Config:
        from_attributes = True
        extra = "forbid"
        
        
# Refresh Token Response Schema
class RefreshTokenResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    token: str
    expires_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = { ObjectId: str }