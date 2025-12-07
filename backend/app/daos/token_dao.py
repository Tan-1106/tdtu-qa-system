import asyncio
from pwdlib import PasswordHash
from datetime import datetime, timezone

from app.databases import mongo
from app.schemas import auth_schema
from app.utils.api_response import DatabaseException, AuthException


class TokenDAO:
    def __init__(self):
        self.tokens_collection = mongo.get_tokens_collection()


    # Store new tokens
    async def create_tokens(self, sub: str, hashed_access_token: str, hashed_refresh_token: str) -> auth_schema.TokensRecord:
        token_data = {
            "sub": sub,
            "access_token": hashed_access_token,
            "refresh_token": hashed_refresh_token,
            "revoked": False,
            "created_at": datetime.now(timezone.utc),
            "revoked_at": None
        }
        result = await self.tokens_collection.insert_one(token_data)
        created_token = await self.tokens_collection.find_one({"_id": result.inserted_id})
        if not created_token:
            raise DatabaseException("Unable to create token record.")
        return auth_schema.TokensRecord(**created_token)
    
    
    # Revoke all tokens of a user
    async def revoke_all_tokens_of_user(self, sub: str) -> bool:
        result = await self.tokens_collection.update_many(
            {"sub": sub, "revoked": False},
            {"$set": {"revoked": True, "revoked_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0

    # Revoke tokens
    async def revoke_refresh_token(self, sub: str, refresh_token: str) -> bool:
        hasher = PasswordHash.recommended()
        tokens = await self.tokens_collection.find({"sub": sub}).to_list(length=None)
        
        for token in tokens:
            is_match = await asyncio.to_thread(hasher.verify, refresh_token, token["refresh_token"])
            
            if is_match and not token["revoked"]:
                result = await self.tokens_collection.update_one(
                    {"_id": token["_id"]},
                    {"$set": {"revoked": True, "revoked_at": datetime.now(timezone.utc)}}
                )
                if result.modified_count != 1:
                    raise DatabaseException("Unable to revoke refresh token.")
                return True
            
            elif is_match and token["revoked"]:
                raise AuthException("Refresh token has already been revoked.")
        raise DatabaseException("Refresh token not found.")
    
    
    # Check if refresh token is revoked
    async def is_refresh_token_revoked(self, sub: str, hashed_refresh_token: str) -> bool:
        token = await self.tokens_collection.find_one(
            {"sub": sub, "refresh_token": hashed_refresh_token, "revoked": True}
        )
        return token is not None