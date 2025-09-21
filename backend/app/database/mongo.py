import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongodb:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "tdtu_qa_db")

client: AsyncIOMotorClient | None = None
db = None

async def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        await client.admin.command("ping")
        db = client[DB_NAME]
        logging.info(f"✅ Connected to MongoDB at {MONGO_URL}, using database: {DB_NAME}")
    except ConnectionFailure as e:
        logging.error(f"❌ Could not connect to MongoDB: {e}")
        raise e


async def close_mongo_connection():
    global client
    if client:
        client.close()
        logging.info("🔌 MongoDB connection closed.")


def get_documents_collection():
    global db
    if db is None:
        raise RuntimeError("⚠️ Database is not initialized. Did you call connect_to_mongo()?")
    logging.info(f"📂 Accessing collection: documents in database: {DB_NAME}")
    return db["documents"]
