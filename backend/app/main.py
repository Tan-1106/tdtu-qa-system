import logging
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.api_response import api_response, UserError, NotFoundException, DatabaseException, AuthException
from app.databases.mongo import connect_to_mongo, close_mongo_connection
from app.routes import auth_route, user_route, document_route, document_chunk_route, embedding_route, qa_route, statistical_route
from app.routes import llm_route


# --- LOGGER SETUP ---
logger = logging.getLogger("SystemLogger")


# --- FILTER OUT HEALTH CHECK LOGS ---
class HealthCheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("GET / ") == -1
logger.addFilter(HealthCheckFilter())


# --- LIFESPAN EVENT ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


# --- FASTAPI APP ---
app = FastAPI(
    title="Question-Answering System for TDTU Students",
    lifespan=lifespan
)
    
    
# --- CORS MIDDLEWARE ---
origins = [
    "http://localhost:5173",  
    "http://localhost",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)


# --- EXCEPTION HANDLERS ---
# Authentication Exception
@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    return api_response(
        status_code=401,
        message="Authentication Error",
        details=exc.message
    )


# User Error
@app.exception_handler(UserError)
async def user_error_handler(request, exc: UserError):
    return api_response(
        status_code=400,
        message="User Error",
        details=exc.message
    )
        

# Not Found Exception
@app.exception_handler(NotFoundException)
async def not_found_handler(request, exc: NotFoundException):
    return api_response(
        status_code=404, 
        message="Resource Not Found",
        details=exc.message
    )



# Validation Error
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return api_response(
        status_code=422,
        message="Validation Error",
        details=exc.errors()
    )


# Unhandled Exception
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return api_response(
        status_code=500,
        message="Internal Server Error",
        details="An unexpected error occurred"
    )


# Database Exception
@app.exception_handler(DatabaseException)
async def db_handler(request, exc: DatabaseException):
    return api_response(
        status_code=500, 
        message="Database error",
        details=exc.message
    )
    
    
# HTTP Exception
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return api_response(
        status_code=exc.status_code,
        message="HTTP Exception",
        details=exc.detail
    )


# --- ROOT ENDPOINT ---
@app.get("/")
async def home():
    return {"msg": "Welcome to the TDTU QA System API"}


# --- ROUTES ---
# Authentication routes
app.include_router(auth_route.router, prefix="/api")


# User routes
app.include_router(user_route.router, prefix="/api")


# LLM Model & API Key routes
app.include_router(llm_route.router, prefix="/api")


# Document routes
app.include_router(document_route.router, prefix="/api")


# Document Chunk routes
app.include_router(document_chunk_route.router, prefix="/api")


# Embedding routes
app.include_router(embedding_route.router, prefix="/api")


# Q&A routes
app.include_router(qa_route.router, prefix="/api")


# Statistical routes
app.include_router(statistical_route.router, prefix="/api")