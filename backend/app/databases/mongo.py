import os
import logging
from pymongo.errors import ConnectionFailure
from motor.motor_asyncio import AsyncIOMotorClient
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# --- CONFIGURATION ---
DB_NAME = os.getenv("MONGO_DB_NAME", "tdtu_qa_db")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongodb:27017")


# --- CLIENT ---
# Connect to MongoDB
client: AsyncIOMotorClient | None = None
db = None

async def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        await client.admin.command("ping")
        db = client[DB_NAME]
        logging.info(f"Connected to MongoDB at {MONGO_URL}, database: {DB_NAME}")
    except ConnectionFailure as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise e


# Close MongoDB connection
async def close_mongo_connection():
    global client
    if client:
        client.close()
        logging.info("Closed MongoDB connection.")


# --- COLLECTIONS ---
# Users collection
def get_users_collection():
    global db
    if db is None:
        raise RuntimeError("Database has not been initialized.")
    logging.info(f"Accessing collection: users in database: {DB_NAME}")
    return db.get_collection("users")


# Refresh tokens collection
def get_tokens_collection():
    global db
    if db is None:
        raise RuntimeError("Database has not been initialized.")
    logging.info(f"Accessing collection: tokens in database: {DB_NAME}")
    return db.get_collection("tokens")


# LLM API Keys collection
def get_api_keys_collection():
    global db
    if db is None:
        raise RuntimeError("Database has not been initialized.")
    logging.info(f"Accessing collection: api_keys in database: {DB_NAME}")
    return db.get_collection("api_keys")


# Documents collection
def get_documents_collection():
    global db
    if db is None:
        raise RuntimeError("Database has not been initialized.")
    logging.info(f"Accessing collection: documents in database: {DB_NAME}")
    return db.get_collection("documents")


# Potential questions collection
def get_potential_questions_collection():
    global db
    if db is None:
        raise RuntimeError("Database has not been initialized.")
    logging.info(f"Accessing collection: potential_questions in database: {DB_NAME}")
    return db.get_collection("potential_questions")


# Questions collection
def get_questions_collection():
    global db
    if db is None:
        raise RuntimeError("Database has not been initialized.")
    logging.info(f"Accessing collection: questions in database: {DB_NAME}")
    return db.get_collection("questions")


# Answers collection
def get_answers_collection():
    global db
    if db is None:
        raise RuntimeError("Database has not been initialized.")
    logging.info(f"Accessing collection: answers in database: {DB_NAME}")
    return db.get_collection("answers")


# Popular questions collection
def get_popular_questions_collection():
    global db
    if db is None:
        raise RuntimeError("Database has not been initialized.")
    logging.info(f"Accessing collection: popular_questions in database: {DB_NAME}")
    return db.get_collection("popular_questions")
