import os
import logging
from pymongo.errors import ConnectionFailure
from motor.motor_asyncio import AsyncIOMotorClient


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# --- CONFIGURATION ---
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongodb:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "tdtu_qa_db")


# --- CLIENT ---
# Kết nối MongoDB
client: AsyncIOMotorClient | None = None
db = None

async def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        await client.admin.command("ping")
        db = client[DB_NAME]
        logging.info(f"- LOG: Đã kết nối đến MongoDB tại {MONGO_URL}, database: {DB_NAME}")
    except ConnectionFailure as e:
        logging.error(f"- LOG: Không thể kết nối đến MongoDB: {e}")
        raise e


# Đóng kết nối MongoDB
async def close_mongo_connection():
    global client
    if client:
        client.close()
        logging.info("- LOG: Đã đóng kết nối MongoDB.")


# --- COLLECTIONS ---
# Users collection
def get_users_collection():
    global db
    if db is None:
        raise RuntimeError("Cơ sở dữ liệu chưa được khởi tạo.")
    logging.info(f"- LOG: Truy cập collection: users trong database: {DB_NAME}")
    return db.get_collection("users")


# Refresh tokens collection
def get_refresh_tokens_collection():
    global db
    if db is None:
        raise RuntimeError("Cơ sở dữ liệu chưa được khởi tạo.")
    logging.info(f"- LOG: Truy cập collection: refresh_tokens trong database: {DB_NAME}")
    return db.get_collection("refresh_tokens")


# Documents collection
def get_documents_collection():
    global db
    if db is None:
        raise RuntimeError("Cơ sở dữ liệu chưa được khởi tạo.")
    logging.info(f"- LOG: Truy cập collection: documents trong database: {DB_NAME}")
    return db.get_collection("documents")


# Potential questions collection
def get_potential_questions_collection():
    global db
    if db is None:
        raise RuntimeError("Cơ sở dữ liệu chưa được khởi tạo.")
    logging.info(f"- LOG: Truy cập collection: potential_questions trong database: {DB_NAME}")
    return db.get_collection("potential_questions")


# Questions collection
def get_questions_collection():
    global db
    if db is None:
        raise RuntimeError("Cơ sở dữ liệu chưa được khởi tạo.")
    logging.info(f"- LOG: Truy cập collection: questions trong database: {DB_NAME}")
    return db.get_collection("questions")


# Answers collection
def get_answers_collection():
    global db
    if db is None:
        raise RuntimeError("Cơ sở dữ liệu chưa được khởi tạo.")
    logging.info(f"- LOG: Truy cập collection: answers trong database: {DB_NAME}")
    return db.get_collection("answers")


# Popular questions collection
def get_popular_questions_collection():
    global db
    if db is None:
        raise RuntimeError("Cơ sở dữ liệu chưa được khởi tạo.")
    logging.info(f"- LOG: Truy cập collection: popular_questions trong database: {DB_NAME}")
    return db.get_collection("popular_questions")
