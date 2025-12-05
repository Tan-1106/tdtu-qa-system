from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app.services import auth_service
from app.controllers import auth_controller
from app.utils.api_response import api_response
from app.schemas import auth_schema, user_schema


# --- ROUTER ---
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# --- ROUTES ---
# Process ELIT login
@router.post("/verify")
async def elit_login(code: auth_schema.ELITLoginCode):
    code = jsonable_encoder(code)["code"]
    response = await auth_controller.elit_login(code)
    
    print("ELIT LOGIN RESPONSE:", response)
    return api_response(
        status_code=200,
        message="Login successful",
        details=response
    )
        
            
# Get current user information
@router.get("/me")
async def get_current_user(current_user: user_schema.UserRecord = Depends(auth_service.get_current_user)):
    return api_response(
        status_code=200,
        message="Get current user information successful",
        details=current_user
    )
        
        
# Refresh Tokens
@router.post("/refresh")
async def refresh_tokens(refresh_token: auth_schema.RefreshTokensRequest):
    refresh_token = jsonable_encoder(refresh_token)["refresh_token"]
    tokens = await auth_controller.refresh_tokens(refresh_token)
    return api_response(
        status_code=200,
        message="Refresh tokens successful.",
        details=tokens
    )