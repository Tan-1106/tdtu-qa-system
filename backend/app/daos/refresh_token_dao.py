from pwdlib import PasswordHash
from datetime import datetime, timezone
from fastapi.encoders import jsonable_encoder

from app.databases import mongo
from app.schemas import refresh_token_schema

hasher = PasswordHash.recommended()

# Create a new refresh token
async def store_refresh_token(token_data: refresh_token_schema.RefreshTokenCreate) -> bool:
    token_data = jsonable_encoder(token_data)
    token_data["created_at"] = datetime.now(timezone.utc)
    token_data["revoked"] = False
    
    result = await mongo.get_refresh_tokens_collection().insert_one(token_data)
    created_token = await mongo.get_refresh_tokens_collection().find_one({"_id": result.inserted_id})
    return created_token is not None


# Revoke a refresh token
async def revoke_refresh_token(user_id: str, refresh_token: str) -> bool:
    hashed_tokens = await mongo.get_refresh_tokens_collection().find(
        {"user_id": user_id, "revoked": False}
    ).to_list(length=None)
    
    for token in hashed_tokens:
        if hasher.verify(refresh_token, token["hashed_token"]):
            update_result = await mongo.get_refresh_tokens_collection().update_one(
                {"_id": token["_id"]},
                {"$set": {"revoked": True, "revoked_at": datetime.now(timezone.utc)}}
            )
            return update_result.modified_count == 1
    return False
    

# Check if a refresh token is revoked
async def is_refresh_token_revoked(user_id: str, refresh_token: str) -> bool:
    hashed_tokens = await mongo.get_refresh_tokens_collection().find(
        {"user_id": user_id, "revoked": True}
    ).to_list(length=None)
    
    for token in hashed_tokens or []:
        if hasher.verify(refresh_token, token["hashed_token"]):
            return True
    return False   