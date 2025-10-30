import os
import logging
from pymongo.errors import ConnectionFailure
from motor.motor_asyncio import AsyncIOMotorClient

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Đọc biến môi trường
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongodb:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "tdtu_qa_db")

# Kết nối MongoDB
client: AsyncIOMotorClient | None = None
db = None

async def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        await client.admin.command("ping")
        db = client[DB_NAME]
        logging.info(f"LOG: Connected to MongoDB at {MONGO_URL}, using database: {DB_NAME}")
    except ConnectionFailure as e:
        logging.error(f"LOG: Could not connect to MongoDB: {e}")
        raise e

# Đóng kết nối MongoDB
async def close_mongo_connection():
    global client
    if client:
        client.close()
        logging.info("LOG: MongoDB connection closed.")

# COLLECTIONS
# Users collection
def get_users_collection():
    global db
    if db is None:
        raise RuntimeError("Database is not initialized. Did you call connect_to_mongo()?")
    logging.info(f"LOG: Accessing collection: users in database: {DB_NAME}")
    return db.get_collection("users")

# Documents collection
def get_documents_collection():
    global db
    if db is None:
        raise RuntimeError("Database is not initialized. Did you call connect_to_mongo()?")
    logging.info(f"LOG: Accessing collection: documents in database: {DB_NAME}")
    return db.get_collection("documents")

# Potential questions collection
def get_potential_questions_collection():
    global db
    if db is None:
        raise RuntimeError("Database is not initialized. Did you call connect_to_mongo()?")
    logging.info(f"LOG: Accessing collection: potential_questions in database: {DB_NAME}")
    return db.get_collection("potential_questions")

# Questions collection
def get_questions_collection():
    global db
    if db is None:
        raise RuntimeError("Database is not initialized. Did you call connect_to_mongo()?")
    logging.info(f"LOG: Accessing collection: questions in database: {DB_NAME}")
    return db.get_collection("questions")

# Answers collection
def get_answers_collection():
    global db
    if db is None:
        raise RuntimeError("Database is not initialized. Did you call connect_to_mongo()?")
    logging.info(f"LOG: Accessing collection: answers in database: {DB_NAME}")
    return db.get_collection("answers")

# Popular questions collection
def get_popular_questions_collection():
    global db
    if db is None:
        raise RuntimeError("Database is not initialized. Did you call connect_to_mongo()?")
    logging.info(f"LOG: Accessing collection: popular_questions in database: {DB_NAME}")
    return db.get_collection("popular_questions")
