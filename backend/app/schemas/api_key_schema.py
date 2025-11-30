from enum import Enum
from bson import ObjectId
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


# API Key Record Schema
class APIKeyRecord(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: str | None = None
    api_key: str
    provider: str
    is_using: bool
    created_at: datetime
    updated_at: datetime | None = None
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = { ObjectId: str }
        

#  API Key Creation Schema
class APIKeyCreationSchema(BaseModel):
    name: str
    description: str | None = None
    api_key: str
    provider: str
    class Config:
        from_attributes = True
        extra = "forbid"    
        
        
# API Key Update Schema
class APIKeyUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    api_key: Optional[str] = None
    provider: Optional[str] = None
    class Config:
        from_attributes = True
        extra = "forbid"
        
        
# API Key Usage Toggle Schema
class APIKeyUsageToggleSchema(BaseModel):
    is_using: bool
    class Config:
        from_attributes = True
        extra = "forbid"
        
        
# Enum for API Key Providers
class APIKeyProvider(str, Enum):
    OPENAI = "OpenAI"
    GEMINI = "Google"