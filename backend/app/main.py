from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routers import document, question_embedding
from app.utils.api_response import error_response
from app.database.mongo import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()
    
app = FastAPI(
    title="Question-Answering System for TDTU Students",
    lifespan=lifespan
)
    
# Validation Error
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(
        message="Validation Error",
        status_code=422,
        details=exc.errors()
    )

# HTTPException
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return error_response(
        message=str(exc.detail) if exc.detail else "HTTP error",
        status_code=exc.status_code,
        details=None
    )

# Unhandled Exception
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return error_response(
        message="Internal Server Error",
        status_code=500,
        details=str(exc)
    )

# Root endpoint (For testing)
@app.get("/")
async def home():
    return {"msg": "Welcome to the TDTU QA System API"}

# Thiết lập router
app.include_router(document.router)
app.include_router(question_embedding.router)