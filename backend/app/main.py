from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database.mongo import connect_to_mongo, close_mongo_connection

from app.routes import document_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title="Question-Answering System for TDTU Students",
    lifespan=lifespan
)

@app.get("/")
async def home():
    return {"msg": "Welcome to the TDTU QA System API"}

# Include document routes
app.include_router(document_routes.router, prefix="/documents", tags=["documents"])