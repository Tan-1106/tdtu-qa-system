import os
import jwt
from typing import Annotated
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone

from app.daos import user_dao
from app.schemas import auth_schema

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
EXPIRATION_TIME_MINUTES=int(os.getenv("EXPIRATION_TIME_MINUTES"))

password_hasher = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Register a new user
async def register_user(user_data: dict) -> dict:
    user_data["password"] = password_hasher.hash(user_data["password"])
    user_data["role"] = "User"
    user = await user_dao.create_user(user_data)
    return user

# Authenticate user and generate token
async def authenticate_user(request: dict) -> dict:
    email = request["email"]
    password = request["password"]
    
    user = await user_dao.get_user_by_email(email)
    user = jsonable_encoder(user)
    
    if not password_hasher.verify(password, user["password"]):
        raise ValueError("Wrong password")

    token = await generate_token(user)
    return {"access_token": token, "token_type": "bearer"}

# Generate JWT token
async def generate_token(user: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRATION_TIME_MINUTES)
    
    payload = auth_schema.TokenData(
        full_name=user["full_name"],
        email=user["email"],
        role=user["role"],
        exp=expire
    ).model_dump()

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Get current user from token
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email is None:
            raise credentials_exception
        
        user = await user_dao.get_user_by_email(email)
        if user is None:
            raise credentials_exception
        return user
       
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) 
        
    except jwt.InvalidTokenError:
        raise credentials_exception

# Role-based access control
def require_role(required_role: list[str]):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        current_user = jsonable_encoder(current_user)
        if current_user["role"] not in required_role:
            raise HTTPException(
                status_code=403,
                detail="Operation not permitted"
            )
        return current_user
    return role_checker

# Verify self action or admin
def require_self_or_admin():
    async def self_or_admin_checker(user_id: str, current_user: dict = Depends(get_current_user)):
        current_user = jsonable_encoder(current_user)
        if current_user["role"] != "Admin" and str(current_user["_id"]) != user_id:
            raise HTTPException(
                status_code=403,
                detail="Operation not permitted"
            )
        return current_user
    return self_or_admin_checker