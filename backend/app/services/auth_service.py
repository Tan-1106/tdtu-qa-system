import os
import jwt
import httpx
import base64
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


CLIENT_ID = os.getenv("ELIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("ELIT_CLIENT_SECRET")

AUTH_BASE = os.getenv("ELIT_BASE_URL")
REDIRECT_URI = os.getenv("CALLBACK_URL")


# --- ELIT OAUTH2 ---
async def elit_login(code: str) -> dict:
    if not code or not isinstance(code, str):
        raise ValueError("Mã code không hợp lệ.")

    
    if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_BASE]):
        raise Exception("Lỗi hệ thống: Cấu hình đăng nhập chưa đầy đủ.")

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
            raise Exception(f"Không gọi được ELIT token endpoint: {str(e)}")

    if res.status_code >= 400:
        try:
            err = res.json()
        except Exception:
            err = {"message": f"ELIT trả về lỗi {res.status_code}"}
        raise ValueError(err.get("message") or "Không thể lấy token từ ELIT.")

    try:
        data = res.json()
    except Exception as e:
        raise Exception(f"Không phân tích được phản hồi từ ELIT: {str(e)}")

    print("ELIT token response data:", data)
    return data

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