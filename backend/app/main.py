import logging
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.api_response import api_response
from app.databases.mongo import connect_to_mongo, close_mongo_connection
from app.routes import document_route, question_embedding_route, user_route, prototype_route, auth_route, question_route, potential_question_route


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
        details="An unexpected error occurred."
    )


# --- ROOT ENDPOINT ---
@app.get("/")
async def home():
    return {"msg": "Welcome to the TDTU QA System API"}


# # --- ROUTES ---
# # Authentication routes
# app.include_router(auth_route.router, prefix="/api")


# # User routes
# app.include_router(user_route.user_router, prefix="/api")
# app.include_router(user_route.admin_router, prefix="/api")


# # Document routes
# app.include_router(document_route.user_route, prefix="/api")
# app.include_router(document_route.admin_route, prefix="/api")


# # Question Embedding routes
# app.include_router(question_embedding_route.router, prefix="/api")


# # Prototype routes
# app.include_router(prototype_route.router, prefix="/api")


# # Potential Question routes
# app.include_router(potential_question_route.route, prefix="/api")


# # Question routes
# app.include_router(question_route.user_router, prefix="/api")
# app.include_router(question_route.admin_router, prefix="/api")