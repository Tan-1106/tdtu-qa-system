import os
import jwt
from typing import Annotated
from pwdlib import PasswordHash
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status

from app.daos import user_dao, refresh_token_dao

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_EXPIRATION_TIME_MINUTES=int(os.getenv("ACCESS_EXPIRATION_TIME_MINUTES") or 5)
REFRESH_EXPIRATION_TIME_DAYS=int(os.getenv("REFRESH_EXPIRATION_TIME_DAYS") or 7)

hasher = PasswordHash.recommended()
oauth2_access_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- TOKEN ---
# Generate JWT Token
async def generate_token(user: dict) -> str:
    now = datetime.now(timezone.utc)
    
    # Access token
    access_payload = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
        "type": "access",
        "exp": now + timedelta(minutes=ACCESS_EXPIRATION_TIME_MINUTES),
        "iat": now
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # Refresh token
    refresh_payload = {
        "sub": str(user["_id"]),
        "type": "refresh",
        "exp": now + timedelta(days=REFRESH_EXPIRATION_TIME_DAYS),
        "iat": now
    }
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return access_token, refresh_token


# Verify Access Token
async def verify_access_token(token: str = Depends(oauth2_access_scheme)) -> dict:
    if not token:
        raise ValueError("Access token missing")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise ValueError("Invalid token type")

        user_id = payload.get("sub")
        user = await user_dao.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User not found")

        return {
            "token": token,
            "payload": payload
        }
    except jwt.ExpiredSignatureError:
        raise Exception("Access token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Could not validate credentials")
        
        
# Verify Refresh Token
async def verify_refresh_token(refresh_token: str) -> dict:
    if not refresh_token:
        raise ValueError("Refresh token missing")
        
    try:
        print("Decoding refresh token...")
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise Exception("Invalid token type")
        
        print("Refresh token payload decoded successfully.")
        user_id = payload.get("sub")
        print("User ID from refresh token payload:", user_id)
        user = await user_dao.get_user_by_id(user_id)
        if not user:
            raise Exception("User not found")
            
        return {
            "token": refresh_token,
            "payload": payload
        }
    except jwt.ExpiredSignatureError:
        raise Exception("Refresh token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Could not validate credentials")


# Refresh Access Token And Refresh Token
async def refresh_tokens(refresh_token: str) -> str:
    print("Verifying refresh token...")
    refresh_token = await verify_refresh_token(refresh_token)
    now = datetime.now(timezone.utc)
    
    print("Refresh token verified. Checking revocation status...")
    user_id = refresh_token["payload"]["sub"]
    user = await user_dao.get_user_by_id(user_id)
    user = jsonable_encoder(user)
    if not user:
        raise Exception("User not found")
        
    revoked_refresh_token = await refresh_token_dao.is_refresh_token_revoked(user_id, refresh_token["token"])
    if revoked_refresh_token:
        raise Exception("Refresh token has been revoked")
        
    # New Access Token
    new_access_payload = {
        "sub": user_id,
        "email": user["email"],
        "role": user["role"],
        "type": "access",
        "exp": now + timedelta(minutes=ACCESS_EXPIRATION_TIME_MINUTES),
        "iat": now
    }
    new_access_token = jwt.encode(new_access_payload, SECRET_KEY, algorithm=ALGORITHM)
    print("new_access_token:", new_access_token)
    
    # New Refresh Token
    rt_revoked = await refresh_token_dao.revoke_refresh_token(user_id, refresh_token["token"])
    print("rt_revoked:", rt_revoked)
    if not rt_revoked:
        raise Exception("Failed to revoke refresh token")
        
    new_refresh_payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": now + timedelta(days=REFRESH_EXPIRATION_TIME_DAYS),
        "iat": now
    }
    new_refresh_token = jwt.encode(new_refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
    success = await refresh_token_dao.store_refresh_token(
        {
            "user_id": str(user["_id"]),
            "hashed_token": hasher.hash(new_refresh_token)
        }
    )
    if not success:
        raise Exception("Failed to store new refresh token")
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
    }
        
        
# --- AUTHENTICATION ---
# Register
async def register_user(user_data: dict) -> dict:
    user_data["password"] = hasher.hash(user_data["password"])
    user_data["role"] = "User"
    user = await user_dao.create_user(user_data)
    return user


# Login And Generate Tokens
async def login(request: dict) -> dict:    
    email = request["email"]
    password = request["password"]
        
    user_credentials = await user_dao.get_user_credentials_by_email(email)
    user_credentials = jsonable_encoder(user_credentials)
    try:
        if not hasher.verify(password, user_credentials["password"]):
            raise ValueError("Wrong password")
    except ValueError as e:
        raise ValueError("Wrong password or unsupported hash format") from e

    access_token, refresh_token = await generate_token(user_credentials)
    
    success = await refresh_token_dao.store_refresh_token(
        {
            "user_id": str(user_credentials["_id"]),
            "hashed_token": hasher.hash(refresh_token)
        }
    )
    if not success:
        raise Exception("Authentication failed")
    
    return {
        "token": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        },
        "user": {
            "full_name": user_credentials["full_name"],
            "email": user_credentials["email"],
            "role": user_credentials["role"]
        }
    }


# Get Current User
async def get_current_user(access_token: dict = Depends(verify_access_token)) -> dict:
    user_id = access_token["payload"]["sub"]
    user = await user_dao.get_user_by_id(user_id)
    if not user:
        raise Exception("User not found")
    user = jsonable_encoder(user)
    return user


# Role-based Access Control
def require_role(required_role: list[str]):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        current_user = jsonable_encoder(current_user)
        if current_user["role"] not in required_role:
            raise Exception("Operation not permitted")
        return current_user
    return role_checker
    
    
# Verify Self Action or Admin
def require_self_or_admin():
    async def self_or_admin_checker(user_id: str, current_user: dict = Depends(get_current_user)):
        current_user = jsonable_encoder(current_user)
        if current_user["role"] != "Admin" and str(current_user["_id"]) != user_id:
            raise Exception("Operation not permitted")
        return current_user
    return self_or_admin_checker 