# import base64
# import os
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# import httpx


# class TokenRequest(BaseModel):
#     code: str


# router = APIRouter(prefix="/elit", tags=["ELIT Auth"])


# @router.post("/token")
# async def exchange_token(payload: TokenRequest):
#     client_id = os.getenv("ELIT_CLIENT_ID")
#     client_secret = os.getenv("ELIT_CLIENT_SECRET")
#     redirect_uri = os.getenv("ELIT_CALLBACK_URL")
#     auth_base = os.getenv("ELIT_AUTH_BASE")

#     if not all([client_id, client_secret, redirect_uri, auth_base]):
#         raise HTTPException(status_code=500, detail="ELIT auth environment is not configured")

#     token_url = auth_base.rstrip("/") + "/oauth2/v1/token"
#     basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
#     headers = {"Authorization": f"Basic {basic}", "Content-Type": "application/json"}
#     data = {"code": payload.code, "grant_type": "authorization_code", "redirect_uri": redirect_uri}

#     async with httpx.AsyncClient(timeout=20) as client:
#         try:
#             resp = await client.post(token_url, json=data, headers=headers)
#         except httpx.RequestError as e:
#             raise HTTPException(status_code=502, detail=f"ELIT token request failed: {str(e)}")

#     if resp.status_code >= 400:
#         # Expecting error body like {"message": "..."}
#         try:
#             err = resp.json()
#         except Exception:
#             err = {"message": f"ELIT error {resp.status_code}"}
#         raise HTTPException(status_code=resp.status_code, detail=err.get("message", "Token exchange failed"))

#     return resp.json()