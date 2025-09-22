from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database.mongo import connect_to_mongo, close_mongo_connection
from app.routers import documents

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

# Thiết lập router
app.include_router(documents.router)