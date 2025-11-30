# User
def user_serialize(user) -> dict:
    return {
        "id": str(user["_id"]),
        "sub": str(user["sub"]),
        "name": user.get("name"),
        "email": user.get("email"),
        "image": user.get("image"),
        "role": user.get("role"),
        "faculty": user.get("faculty"),
        "banned": user.get("banned", False),
        "created_at": user.get("created_at").isoformat() if user.get("created_at") else None
    }
    

# Tokens
def tokens_serialize(tokens) -> dict:
    return {
        "access_token": tokens.get("access_token"),
        "refresh_token": tokens.get("refresh_token"),
        "revoked": tokens.get("revoked", False),
        "created_at": tokens.get("created_at").isoformat() if tokens.get("created_at") else None,
        "revoked_at": tokens.get("revoked_at").isoformat() if tokens.get("revoked_at") else None
    }
    

# API Key
def api_key_serialize(api_key) -> dict:
    return {
        "id": str(api_key["_id"]),
        "name": api_key.get("name"),
        "description": api_key.get("description"),
        "api_key": api_key.get("api_key"),
        "provider": api_key.get("provider"),
        "is_using": api_key.get("is_using", False),
        "created_at": api_key.get("created_at").isoformat() if api_key.get("created_at") else None,
        "updated_at": api_key.get("updated_at").isoformat() if api_key.get("updated_at") else None
    }