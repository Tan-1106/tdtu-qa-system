from pydantic import BaseModel
from typing import Optional, Any
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class SuccessResponse(BaseModel):
    status_code: int
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    status_code: int
    message: str
    details: Optional[Any] = None
    
def success_response(message: str, data: Any = None, status_code: int = 200):
    return JSONResponse(
        status_code=status_code,
        content=SuccessResponse(
            status_code=status_code,
            message=message,
            data=jsonable_encoder(data)
        ).model_dump()
    )

def error_response(message: str, details: Any = None, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            status_code=status_code,
            message=message,
            details=details
        ).model_dump()
    )