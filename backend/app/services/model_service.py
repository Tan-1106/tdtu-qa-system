import os
import re
import asyncio
import logging
from openai import OpenAI
from pyvi.ViTokenizer import tokenize
from cryptography.fernet import Fernet
from fastapi.encoders import jsonable_encoder
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer, CrossEncoder
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

from app.daos.api_key_dao import APIKeyDAO
from app.utils.api_response import DatabaseException


# --- CONFIGURATION ---


# --- API KEYS SERVICE ---
# API Key Encryptor
class APIKeyEncryptor:
    def __init__(self):
        key = os.getenv("API_KEY_SECRET")
        self.fernet = Fernet(key)

    def encrypt(self, api_key: str) -> str:
        return self.fernet.encrypt(api_key.encode()).decode()

    def decrypt(self, encrypted_api_key: str) -> str:
        return self.fernet.decrypt(encrypted_api_key.encode()).decode()


# Create a new API key
async def create_api_key(data: dict):
    encryptor = APIKeyEncryptor()
    
    # Check if API key already exists
    existing_keys = jsonable_encoder(await APIKeyDAO().get_all_api_keys())
    for encrypted_key in existing_keys:
        decrypted_key = encryptor.decrypt(encrypted_key["api_key"])
        if decrypted_key == data["api_key"]:
            raise DatabaseException("API key already exists.")
    
    # Encrypt the API key before storing
    encrypted = encryptor.encrypt(data["api_key"])
    data["api_key"] = encrypted
    
    api_key = jsonable_encoder(await APIKeyDAO().create_api_key(data))
    api_key["api_key"] = encryptor.decrypt(api_key["api_key"])
    
    return api_key
    

# Get all API keys
async def get_all_api_keys(page: int, limit: int):
    encryptor = APIKeyEncryptor()
    
    skip = (page - 1) * limit
    total = await APIKeyDAO().count_all_api_keys()
    total_pages = (total + limit - 1) // limit
    if total == 0:
        return {
            "api_keys": [],
            "total": 0,
            "total_pages": 0,
            "current_page": page
        }
    
    api_keys = jsonable_encoder(await APIKeyDAO().get_api_keys(skip, limit))
    for api_key in api_keys:
        decrypted = encryptor.decrypt(api_key["api_key"])
        api_key["api_key"] = decrypted
    return {
        "api_keys": api_keys,
        "total": total,
        "total_pages": total_pages,
        "current_page": page
    }
    
    
# Update an existing API key
async def update_api_key(key_id: str, update_data: dict):
    encryptor = APIKeyEncryptor()
    
    # Check if API key already exists
    if "api_key" in update_data:
        existing_keys = jsonable_encoder(await APIKeyDAO().get_all_api_keys())
        for encrypted_key in existing_keys:
            decrypted_key = encryptor.decrypt(encrypted_key["api_key"])
            if decrypted_key == update_data["api_key"]:
                raise DatabaseException("API key already exists.")
        update_data["api_key"] = encryptor.encrypt(update_data["api_key"])
    
    updated_key = jsonable_encoder(await APIKeyDAO().update_api_key(key_id, update_data))
    decrypted = encryptor.decrypt(updated_key["api_key"])
    updated_key["api_key"] = decrypted
    
    return updated_key

# --- MODELS SERVICE ---