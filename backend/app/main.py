from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routes import document_route
from app.routes import question_embedding_route
from app.utils.api_response import api_response
from app.databases.mongo import connect_to_mongo, close_mongo_connection


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
    return api_response(
        status_code=422,
        message="Validation Error",
        details=exc.errors()
    )

# HTTPException
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return api_response(
        status_code=exc.status_code,
        message=str(exc.detail) if exc.detail else "HTTP error",
        details=None
    )

# Unhandled Exception
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return api_response(
        status_code=500,
        message="Internal Server Error",
        details=str(exc)
    )

# Root endpoint (For testing)
@app.get("/")
async def home():
    return {"msg": "Welcome to the TDTU QA System API"}

# Thiết lập router
app.include_router(document_route.router)
app.include_router(question_embedding_route.router)