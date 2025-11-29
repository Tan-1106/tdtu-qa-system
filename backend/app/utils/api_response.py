from typing import Any
from fastapi.responses import JSONResponse


def api_response(status_code: int, message: str, details: Any = None):
    return JSONResponse(
        status_code = status_code,
        success = 200 <= status_code < 300, 
        content={
            "message": message,
            "details": details
        }
    )