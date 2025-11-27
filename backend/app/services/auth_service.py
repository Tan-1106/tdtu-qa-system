import os
import jwt
from fastapi import Depends
from pwdlib import PasswordHash
from fastapi.encoders import jsonable_encoder
from itsdangerous import URLSafeTimedSerializer
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone

from app.daos import user_dao, refresh_token_dao


SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_EXPIRATION_TIME_MINUTES=int(os.getenv("ACCESS_EXPIRATION_TIME_MINUTES") or 5)
REFRESH_EXPIRATION_TIME_DAYS=int(os.getenv("REFRESH_EXPIRATION_TIME_DAYS") or 7)


hasher = PasswordHash.recommended()
oauth2_access_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
reset_password_serializer = URLSafeTimedSerializer(SECRET_KEY)

# --- TOKEN ---
# Tạo JWT Tokens
async def generate_tokens(user: dict) -> str:
    now = datetime.now(timezone.utc)
    
    # Access Token
    access_payload = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
        "type": "access",
        "exp": now + timedelta(minutes=ACCESS_EXPIRATION_TIME_MINUTES),
        "iat": now
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # Refresh Token
    refresh_payload = {
        "sub": str(user["_id"]),
        "type": "refresh",
        "exp": now + timedelta(days=REFRESH_EXPIRATION_TIME_DAYS),
        "iat": now
    }
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return access_token, refresh_token


# Xác thực Access Token
async def verify_access_token(token: str = Depends(oauth2_access_scheme)) -> dict:
    if not token:
        raise ValueError("Không tìm thấy access token.")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise ValueError("Loại token không hợp lệ.")

        user_id = payload.get("sub")
        user = await user_dao.get_user_by_id(user_id)
        if user is None:
            raise ValueError("Không tìm thấy người dùng.")

        return {
            "token": token,
            "payload": payload
        }
    except jwt.ExpiredSignatureError:
        raise Exception("Access token đã hết hạn.")
    except jwt.InvalidTokenError:
        raise Exception("Không thể xác thực thông tin đăng nhập.")
        
        
# Xác thực Refresh Token
async def verify_refresh_token(refresh_token: str) -> dict:
    if not refresh_token:
        raise ValueError("Không tìm thấy refresh token.")
        
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise Exception("Loại token không hợp lệ.")
        
        user_id = payload.get("sub")
        user = await user_dao.get_user_by_id(user_id)
        if not user:
            raise Exception("Không tìm thấy người dùng.")
            
        return {
            "token": refresh_token,
            "payload": payload
        }
    except jwt.ExpiredSignatureError:
        raise Exception("Refresh token đã hết hạn.")
    except jwt.InvalidTokenError:
        raise Exception("Không thể xác thực thông tin đăng nhập.")


# Làm mới Tokens
async def refresh_tokens(refresh_token: str) -> str:
    refresh_token = await verify_refresh_token(refresh_token)
    now = datetime.now(timezone.utc)
    
    user_id = refresh_token["payload"]["sub"]
    user = await user_dao.get_user_by_id(user_id)
    user = jsonable_encoder(user)
    if not user:
        raise Exception("Không tìm thấy người dùng.")
        
    revoked_refresh_token = await refresh_token_dao.is_refresh_token_revoked(user_id, refresh_token["token"])
    if revoked_refresh_token:
        raise Exception("Refresh token đã bị thu hồi.")
        
    # Access Token mới
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
    
    # Refresh Token mới
    rt_revoked = await refresh_token_dao.revoke_refresh_token(user_id, refresh_token["token"])
    print("rt_revoked:", rt_revoked)
    if not rt_revoked:
        raise Exception("Không thể thu hồi refresh token.")
        
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
        raise Exception("Không thể lưu refresh token mới.")
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
    }
    
    
# Tạo reset password token
def generate_reset_password_token(email: str) -> str:
    return reset_password_serializer.dumps(email, salt="reset-password")


# Xác minh reset password token
def verify_reset_password_token(token: str, expiration: int = 300) -> str:
    try:
        email = reset_password_serializer.loads(
            token,
            salt="reset-password",
            max_age=expiration
        )
        return email
    except Exception:
        raise ValueError("Token đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.")
        
        
# --- AUTHENTICATION ---
# Đăng ký người dùng mới
async def register_user(user_data: dict) -> dict:
    user_data["password"] = hasher.hash(user_data["password"])
    user_data["role"] = "User"
    user = await user_dao.create_user(user_data)
    return user


# Đăng nhập và tạo tokens
async def login(request: dict) -> dict:    
    email = request["email"]
    password = request["password"]
        
    user_credentials = await user_dao.get_user_credentials_by_email(email)
    user_credentials = jsonable_encoder(user_credentials)
    try:
        if not hasher.verify(password, user_credentials["password"]):
            raise ValueError("Sai mật khẩu.")
    except ValueError as e:
        raise ValueError("Không thể xác thực mật khẩu.") from e

    access_token, refresh_token = await generate_tokens(user_credentials)
    
    success = await refresh_token_dao.store_refresh_token(
        {
            "user_id": str(user_credentials["_id"]),
            "hashed_token": hasher.hash(refresh_token)
        }
    )
    if not success:
        raise Exception("Xác thực đăng nhập không thành công.")
    
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


# Lấy người dùng hiện tại từ Access Token
async def get_current_user(access_token: dict = Depends(verify_access_token)) -> dict:
    user_id = access_token["payload"]["sub"]
    user = await user_dao.get_user_by_id(user_id)
    if not user:
        raise Exception("Không tìm thấy người dùng.")
    user = jsonable_encoder(user)
    return user


# Kiểm tra vai trò người dùng
def require_role(required_role: list[str]):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        current_user = jsonable_encoder(current_user)
        if current_user["role"] not in required_role:
            raise Exception("Không có quyền truy cập.")
        return current_user
    return role_checker
    
    
# Xác minh hành động của chính người dùng hoặc Admin
def require_self_or_admin():
    async def self_or_admin_checker(user_id: str, current_user: dict = Depends(get_current_user)):
        current_user = jsonable_encoder(current_user)
        if current_user["role"] != "Admin" and str(current_user["_id"]) != user_id:
            raise Exception("Không có quyền truy cập.")
        return current_user
    return self_or_admin_checker 