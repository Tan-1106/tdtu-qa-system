from typing import Any
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

# --- API RESPONSE ---
def api_response(status_code: int, message: str, details: Any = None):
    return JSONResponse(
        status_code=status_code,
        content={
            "status_code": status_code,
            "message": message,
            "details": details
        }
    )
    

# --- CUSSTOM EXCEPTIONS ---
class UserError(Exception):
    def __init__(self, message: str = "User error occurred"):
        self.message = message


class NotFoundException(Exception):
    def __init__(self, message: str = "Resource not found"):
        self.message = message


class DatabaseException(Exception):
    def __init__(self, message: str = "Database error"):
        self.message = message
        

class AuthException(Exception):
    def __init__(self, message: str = "Unauthorized"):
        self.message = message