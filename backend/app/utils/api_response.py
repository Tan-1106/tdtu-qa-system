from pydantic import BaseModel
from typing import Optional, Any
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class ApiResponse(BaseModel):
    status_code: int
    message: str
    details: Optional[Any] = None


def api_response(status_code: int, message: str, details: Any = None):
    return JSONResponse(
        status_code=status_code,
        content=ApiResponse(
            status_code=status_code,
            message=message,
            details=jsonable_encoder(details)
        ).model_dump()
    )