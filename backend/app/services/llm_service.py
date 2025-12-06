import os
import re
import ast
import json
import asyncio
import logging
from openai import OpenAI
import google.generativeai as genai
from pyvi.ViTokenizer import tokenize
from cryptography.fernet import Fernet
from fastapi.encoders import jsonable_encoder
from app.utils.text_process import normalize_text
from app.schemas.api_key_schema import APIKeyProvider
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer, CrossEncoder
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

from app.daos.api_key_dao import APIKeyDAO
from app.utils.api_response import UserError, DatabaseException


# --- CONFIGURATION ---
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
async def get_all_api_keys(page: int, limit: int, name: str = None, description: str = None, provider: str = None):
    encryptor = APIKeyEncryptor()
    
    skip = (page - 1) * limit
    total = await APIKeyDAO().count_all_api_keys(name, description, provider)
    total_pages = (total + limit - 1) // limit
    if total == 0:
        return {
            "api_keys": [],
            "total": 0,
            "total_pages": 0,
            "current_page": page
        }
    
    api_keys = jsonable_encoder(await APIKeyDAO().get_api_keys(skip, limit, name, description, provider))
    for api_key in api_keys:
        decrypted = encryptor.decrypt(api_key["api_key"])
        api_key["api_key"] = decrypted
    return {
        "api_keys": api_keys,
        "total": total,
        "total_pages": total_pages,
        "current_page": page
    }
    
    
# Get a single API key by ID
async def get_api_key_by_id(key_id: str):
    encryptor = APIKeyEncryptor()
    
    api_key = jsonable_encoder(await APIKeyDAO().get_api_key_by_id(key_id))
    if not api_key:
        raise DatabaseException("API key not found.")
    
    decrypted = encryptor.decrypt(api_key["api_key"])
    api_key["api_key"] = decrypted
    return api_key


# Get current using API key
async def get_current_api_key():
    encryptor = APIKeyEncryptor()
    
    api_key = jsonable_encoder(await APIKeyDAO().get_current_using_api_key())
    if not api_key:
        return None

    decrypted = encryptor.decrypt(api_key["api_key"])
    api_key["api_key"] = decrypted
    return api_key


# Update an existing API key
async def update_api_key(key_id: str, update_data: dict):
    encryptor = APIKeyEncryptor()    
    updated_key = jsonable_encoder(await APIKeyDAO().update_api_key(key_id, update_data))
    decrypted = encryptor.decrypt(updated_key["api_key"])
    updated_key["api_key"] = decrypted
    
    return updated_key


# Delete an API key
async def delete_api_key(key_id: str):
    await APIKeyDAO().delete_api_key(key_id)
    
    
# Toggle API Key Usage Status
async def toggle_api_key_status(key_id: str):
    encryptor = APIKeyEncryptor()
    
    api_key = jsonable_encoder(await APIKeyDAO().get_api_key_by_id(key_id))
    if not api_key:
        raise DatabaseException("API key not found")
    if not api_key["is_using"] and api_key["using_model"] is None:
        raise UserError("To activate an API key, please provide the model it will be used for")
    
    new_status = not api_key["is_using"]
    if new_status is True:
        await APIKeyDAO().deactivate_all_api_keys()
    update_data = {"is_using": new_status}
    
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
            # Run API call in thread pool to avoid blocking
            def fetch_openai_models():
                openai_client = OpenAI(api_key=api_key)
                models = openai_client.models.list()
                models = [model.id for model in models.data]
                models = [
                    model for model in models
                    if re.search(r"gpt", model, re.IGNORECASE) and
                       not re.search(r"realtime|chatgpt|transcribe|chat|audio|image|preview|codex|instruct", model, re.IGNORECASE)
                ]
                return models
            
            return await asyncio.to_thread(fetch_openai_models)
        except Exception as e:
            raise UserError("Invalid API key or unable to connect to OpenAI.")
    elif provider == APIKeyProvider.GEMINI.value:
        try:
            def fetch_gemini_models():
                genai.configure(api_key=api_key)
                models = jsonable_encoder(genai.list_models())
                models = [model["name"].replace("models/", "") for model in models]
                models = [
                    model for model in models
                    if re.search(r"gemini", model, re.IGNORECASE) and
                       not re.search(r"embedding|preview|image|exp|audio|live", model, re.IGNORECASE)
                ]
                return models
            
            return await asyncio.to_thread(fetch_gemini_models)
        except Exception as ge:
            raise UserError("Invalid API key or unable to connect to Google Generative AI.")
        
        
# Generate potential questions from text chunks
async def generate_potential_questions(api_key: dict, context: str, num_questions: int) -> list[str]:
    prompt = f"""
    Bạn là một trợ lý tạo câu hỏi thông minh.

    Nhiệm vụ:
    Sinh ra đúng {num_questions} câu hỏi tiềm năng đáp ứng toàn bộ tiêu chí sau:
    - Ngắn gọn, rõ ràng, không trùng lặp, tự nhiên.
    - Là những câu hỏi mà một sinh viên tại Trường Đại học Tôn Đức Thắng có thể đặt ra liên quan đến phạm vi, hoạt động, quy định… của trường dựa trên đoạn văn bạn được cung cấp bên dưới bằng hệ thống Retrieval-Augmented Generation (RAG).
    - Không được hỏi dựa theo cú pháp hoặc câu chữ cụ thể trong văn bản, chỉ dựa trên chủ đề có thể được văn bản đề cập.
    - Không được nhắc đến bản thân văn bản hoặc vị trí văn bản (ví dụ: “theo văn bản trên”, “dựa trên nội dung đã cho”, “thông báo này”, “quy định này”,...).
    - Câu hỏi phải có ý nghĩa đầy đủ, người đọc không cần xem đoạn văn bản vẫn hiểu được.
    - Ít nhất phải có 1 câu hỏi tổng quát về chủ đề chính của đoạn văn bản.
    Đoạn văn bản:
    \"\"\"{context}\"\"\"

    Yêu cầu định dạng đầu ra:
    - Trả về **một danh sách Python hợp lệ** chứa đúng {num_questions} chuỗi (string).
    - Không thêm bất kỳ mô tả, giải thích, hoặc ký tự thừa nào khác ngoài danh sách.
    - Ví dụ đầu ra:
    ["Câu hỏi 1", "Câu hỏi 2", ..., "Câu hỏi {num_questions}"]
    """

    output_text = []
    
    if api_key["provider"] == APIKeyProvider.OPENAI.value:
        def call_openai():
            openai_client = OpenAI(api_key=api_key["api_key"])
            response = openai_client.responses.create(
                model=api_key["using_model"],
                input=prompt,
                store=False
            )
            return response.output_text
        
        output_text = await asyncio.to_thread(call_openai)
        output_text = normalize_text(output_text)
        
    elif api_key["provider"] == APIKeyProvider.GEMINI.value:
        def call_gemini():
            genai.configure(api_key=api_key["api_key"])
            model = genai.GenerativeModel(api_key["using_model"])
            response = model.generate_content(
                prompt,
                generation_config={"max_output_tokens": 1024}
            )
            return response.text
        
        output_text = await asyncio.to_thread(call_gemini)
        output_text = normalize_text(output_text)
    
    return output_text