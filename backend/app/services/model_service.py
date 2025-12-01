import os
import re
import asyncio
import logging
from openai import OpenAI
import google.generativeai as genai
from pyvi.ViTokenizer import tokenize
from cryptography.fernet import Fernet
from fastapi.encoders import jsonable_encoder
from app.schemas.api_key_schema import APIKeyProvider
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer, CrossEncoder
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

from app.daos.api_key_dao import APIKeyDAO
from app.utils.api_response import UserError, DatabaseException


# --- CONFIGURATION ---
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "dangvantuan/vietnamese-embedding")
TRANSLATE_MODEL = os.getenv("TRANSLATE_MODEL", "VietAI/envit5-translation")
CROSS_ENCODER_MODEL = os.getenv("CROSS_ENCODER_MODEL", "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")


# Load Models
# translate_tokenizer = AutoTokenizer.from_pretrained(TRANSLATE_MODEL)
# translate_model = AutoModelForSeq2SeqLM.from_pretrained(TRANSLATE_MODEL)
# cross_encoder_model = CrossEncoder(CROSS_ENCODER_MODEL)


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
            if decrypted_key == update_data["api_key"] and str(encrypted_key["_id"]) != key_id:
                raise DatabaseException("API key already exists.")
        update_data["api_key"] = encryptor.encrypt(update_data["api_key"])
    
    updated_key = jsonable_encoder(await APIKeyDAO().update_api_key(key_id, update_data))
    decrypted = encryptor.decrypt(updated_key["api_key"])
    updated_key["api_key"] = decrypted
    
    return updated_key


# Delete an API key
async def delete_api_key(key_id: str):
    await APIKeyDAO().delete_api_key(key_id)
    
    
# Toggle API Key Usage Status
async def toggle_api_key_status(key_id: str, using_model: str | None = None):
    encryptor = APIKeyEncryptor()
    
    updated_key = jsonable_encoder(await APIKeyDAO().get_api_key_by_id(key_id))
    if not updated_key:
        raise DatabaseException("API key not found.")
    
    new_status = not updated_key.get("is_using", True)
    if new_status:
        if using_model is None:
            raise UserError("Using model must be specified when enabling API key usage.")
        
        await APIKeyDAO().reset_all_api_keys_usage()
        update_data = {"is_using": new_status, "using_model": using_model}
    else:
        update_data = {"is_using": new_status, "using_model": None}
        
    updated_key = jsonable_encoder(await APIKeyDAO().update_api_key(key_id, update_data))
    decrypted = encryptor.decrypt(updated_key["api_key"])
    updated_key["api_key"] = decrypted
    return updated_key
    
    
# --- MODELS SERVICE ---
# Get all available models
async def get_available_models(request: dict):
    provider = request["provider"]
    api_key = request["api_key"]
    
    if provider == APIKeyProvider.OPENAI.value:
        try:
            # Try to fetch models from OpenAI
            openai_client = OpenAI(api_key=api_key)
            models = openai_client.models.list()
            models = [model.id for model in models.data]
            models = [
                model for model in models
                if re.search(r"gpt", model, re.IGNORECASE) and
                   not re.search(r"realtime|mini|chatgpt|transcribe|chat|audio|image|preview|codex|instruct", model, re.IGNORECASE)
            ]
            return models
        except Exception as e:
            raise UserError("Invalid API key or unable to fetch models from OpenAI.")
    elif provider == APIKeyProvider.GEMINI.value:
        try:
            genai.configure(api_key=api_key)
            models = jsonable_encoder(genai.list_models())
            models = [model["name"].replace("models/", "") for model in models]
            models = [
                model for model in models
                if re.search(r"gemini", model, re.IGNORECASE) and
                   not re.search(r"embedding|preview|image|exp|audio|live", model, re.IGNORECASE)
            ]
            return models
        except Exception as ge:
            raise UserError("Invalid API key or unable to fetch models from Google Generative AI.")