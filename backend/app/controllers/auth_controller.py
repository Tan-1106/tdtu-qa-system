from app.services import auth_service


# ELIT Login
async def elit_login(code: str) -> dict:
    response = await auth_service.elit_login(code)
    return response


# Refresh tokens
async def refresh_tokens(refresh_token: str) -> dict:
    new_tokens = await auth_service.refresh_tokens(refresh_token)
    return new_tokens