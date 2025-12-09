import os
import jwt
import httpx
import base64
import asyncio
from fastapi import Depends
from pwdlib import PasswordHash
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from app.utils.api_response import NotFoundException, AuthException

from app.schemas import auth_schema
from app.daos.user_dao import UserDAO
from app.daos.token_dao import TokenDAO
from app.utils.basic_information import Role


# --- ELIT CONFIGURATIONS ---
CLIENT_ID = os.getenv("ELIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("ELIT_CLIENT_SECRET")
AUTH_BASE = os.getenv("ELIT_BASE_URL")
REDIRECT_URI = os.getenv("CALLBACK_URL")


# --- SYSTEM CONFIGURATIONS ---
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_EXPIRATION_TIME_MINUTES=int(os.getenv("ACCESS_EXPIRATION_TIME_MINUTES") or 5)
REFRESH_EXPIRATION_TIME_DAYS=int(os.getenv("REFRESH_EXPIRATION_TIME_DAYS") or 7)


hasher = PasswordHash.recommended()
oauth2_access_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


# --- ELIT LOGIN ---
async def elit_login(code: str) -> dict:
    # Validate input
    if not code or not isinstance(code, str):
        raise NotFoundException("Login code is invalid.")
    
    if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_BASE]):
        raise NotFoundException("ELIT configuration is incomplete.")

    # Get user information from ELIT
    basic = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            res = await client.post(
                url=AUTH_BASE.rstrip("/") + "/oauth2/v1/token",
                headers={ "AUTHORIZATION": f"Basic {basic}" },
                data={
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": REDIRECT_URI    
                },
            )
        except httpx.RequestError as e:
            raise Exception(f"Connection error to ELIT: {str(e)}")

    if res.status_code >= 400:
        raise Exception(f"ELIT returned an error when fetching token: {res.status_code} - {res.text}")

    # Process user data
    user_data = auth_schema.ELITLoginResponse(**res.json()).model_dump()   
    
    # Generate tokens and store user & tokens in DB
    user = await UserDAO().create_user(user_data)
    user = jsonable_encoder(user)
    access_token, refresh_token = await generate_tokens(user)
    if (user["banned"]):
        raise AuthException("User is banned from the system.")
    
    # Hash tokens in thread pool to avoid blocking
    hashed_access, hashed_refresh = await asyncio.gather(
        asyncio.to_thread(hasher.hash, access_token),
        asyncio.to_thread(hasher.hash, refresh_token)
    )
    await TokenDAO().create_tokens(user_data["sub"], hashed_access, hashed_refresh)
    
    return {
        "user": user,
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    }
    

# --- TOKEN ---
# Generate JWT Tokens
async def generate_tokens(user_data: dict) -> str:
    now = datetime.now(timezone.utc)
    
    # Access Token
    access_payload = {
        "sub": str(user_data["sub"]),
        "email": user_data["email"],
        "role": user_data["role"],
        "faculty": user_data["faculty"],
        "type": "access",
        "exp": now + timedelta(minutes=ACCESS_EXPIRATION_TIME_MINUTES),
        "iat": now
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # Refresh Token
    refresh_payload = {
        "sub": str(user_data["sub"]),
        "type": "refresh",
        "exp": now + timedelta(days=REFRESH_EXPIRATION_TIME_DAYS),
        "iat": now
    }
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return access_token, refresh_token


# Verify Access Token
async def verify_access_token(token: str = Depends(oauth2_access_scheme)) -> dict:
    if not token:
        raise AuthException("Invalid action (access token not found)")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise AuthException("Invalid token type")

        user_sub = payload.get("sub")
        user = await UserDAO().get_user_by_sub(user_sub)
        if user is None:
            raise AuthException("User not found")

        return {
            "token": token,
            "payload": payload
        }
    
    except jwt.ExpiredSignatureError:
        raise AuthException("Access token has expired")
    except jwt.InvalidTokenError:
        raise AuthException("Unable to authenticate login information")
        
        
# Verify Refresh Token
async def verify_refresh_token(refresh_token: str) -> dict:
    if not refresh_token:
        raise AuthException("Invalid action (refresh token not found)")
        
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise AuthException("Invalid token type")
        
        user_sub = payload.get("sub")
        user = await UserDAO().get_user_by_sub(user_sub)
        if not user:
            raise AuthException("User not found")
            
        return {
            "token": refresh_token,
            "payload": payload
        }
        
    except jwt.ExpiredSignatureError:
        raise AuthException("Refresh token has expired")
    except jwt.InvalidTokenError:
        raise AuthException("Unable to authenticate login information")


# Refresh Tokens
async def refresh_tokens(refresh_token: str) -> str:
    refresh_token = await verify_refresh_token(refresh_token)
    now = datetime.now(timezone.utc)
    
    user_sub = refresh_token["payload"]["sub"]
    user = await UserDAO().get_user_by_sub(user_sub)
    user = jsonable_encoder(user)
    
    # Check if refresh token is revoked (hash in thread to avoid blocking)
    hashed_refresh = await asyncio.to_thread(hasher.hash, refresh_token["token"])
    revoked_refresh_token = await TokenDAO().is_refresh_token_revoked(user_sub, hashed_refresh)
    if revoked_refresh_token:
        raise AuthException("Refresh token has been revoked")
        
    # New Access Token
    new_access_payload = {
        "sub": user_sub,
        "email": user["email"],
        "role": user["role"],
        "type": "access",
        "exp": now + timedelta(minutes=ACCESS_EXPIRATION_TIME_MINUTES),
        "iat": now
    }
    new_access_token = jwt.encode(new_access_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # New Refresh Token
    await TokenDAO().revoke_refresh_token(user_sub, refresh_token["token"])
    new_refresh_payload = {
        "sub": user_sub,
        "type": "refresh",
        "exp": now + timedelta(days=REFRESH_EXPIRATION_TIME_DAYS),
        "iat": now
    }
    new_refresh_token = jwt.encode(new_refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # Hash tokens in thread pool to avoid blocking
    hashed_new_access, hashed_new_refresh = await asyncio.gather(
        asyncio.to_thread(hasher.hash, new_access_token),
        asyncio.to_thread(hasher.hash, new_refresh_token)
    )
    await TokenDAO().create_tokens(user_sub, hashed_new_access, hashed_new_refresh)
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
    }
    
    
# Revoke refresh token
async def revoke_refresh_token(refresh_token: str):
    refresh_token = await verify_refresh_token(refresh_token)
    user_sub = refresh_token["payload"]["sub"]
    await TokenDAO().revoke_refresh_token(user_sub, refresh_token["token"])
    
    
# Revoke all tokens of a user
async def revoke_all_tokens_of_user(sub: str):
    revoked = await TokenDAO().revoke_all_tokens_of_user(sub)
    return revoked

        
# --- SYSTEM AUTHENTICATION ---
# Get current user information
async def get_current_user(access_token: dict = Depends(verify_access_token)) -> dict:
    user_sub = access_token["payload"]["sub"]
    user = await UserDAO().get_user_by_sub(user_sub)
    user = jsonable_encoder(user)
    
    user_role = user["role"]
    user_banned = user["banned"]
    
    if user_role not in (r.value for r in Role):
        raise AuthException("Your role does not have permission to access the system.")
    if user_banned:
        raise AuthException("User is banned from the system.")

    return user


# Check user role
def require_role(allowed_roles: list):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        current_user = jsonable_encoder(current_user)
        if current_user["role"] not in allowed_roles:
            raise AuthException("Permission denied: User does not have the required role.")
        return current_user
    return role_checker

    
# Check user permission by faculty
def has_faculty_access(required_faculty: str):
    async def permission_checker(current_user: dict = Depends(get_current_user)):
        current_user = jsonable_encoder(current_user)
        if current_user["faculty"] != required_faculty:
            raise AuthException("Permission denied: User does not have access to this faculty.")
        return current_user
    return permission_checker