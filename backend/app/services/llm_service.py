import os
import re
import asyncio
import logging
from openai import OpenAI
import google.generativeai as genai
from cryptography.fernet import Fernet
from fastapi.encoders import jsonable_encoder
from app.utils.text_process import normalize_text
from app.schemas.api_key_schema import APIKeyProvider
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

from app.daos.api_key_dao import APIKeyDAO
from app.utils.api_response import UserError, DatabaseException


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
async def get_all_api_keys(page: int, limit: int, keyword: str = None, provider: str = None):
    encryptor = APIKeyEncryptor()
    
    skip = (page - 1) * limit
    total = await APIKeyDAO().count_all_api_keys(keyword, provider)
    total_pages = (total + limit - 1) // limit
    if total == 0:
        return {
            "api_keys": [],
            "total": 0,
            "total_pages": 0,
            "current_page": page
        }
    
    api_keys = jsonable_encoder(await APIKeyDAO().get_api_keys(skip, limit, keyword, provider))
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


# Generate potential questions from text chunks
async def generate_potential_questions_appendix(api_key: dict, context: str, num_questions: int) -> list[str]:
    prompt = f"""
    Bạn là một trợ lý tạo câu hỏi tiềm năng dựa trên nội dung phụ lục quy định được cung cấp.
    
    Nhiệm vụ:
    Sinh ra đúng {num_questions} câu hỏi tiềm năng đáp ứng toàn bộ tiêu chí sau:
    - Ngắn gọn, rõ ràng, không trùng lặp, tự nhiên.
    - Là những câu hỏi mà một sinh viên tại Trường Đại học Tôn Đức Thắng có thể đặt ra liên quan đến quy định, quy chế của trường dựa trên đoạn văn bạn được cung cấp bên dưới bằng hệ thống Retrieval-Augmented Generation (RAG).
    - Không được hỏi dựa theo cú pháp hoặc câu chữ cụ thể trong văn bản, chỉ dựa trên chủ đề có thể được văn bản đề cập.
    - Không được nhắc đến bản thân văn bản hoặc vị trí văn bản (ví dụ: "Theo Description", "theo Content", “dựa trên nội dung đã cho”, “quy định này”,...).
    - Câu hỏi phải có ý nghĩa đầy đủ, người đọc không cần xem đoạn văn bản vẫn hiểu được.
    - Chỉ tạo những câu hỏi trong phạm vi mà phần "Content" của phụ lục đang đề cập đến.
    
    Đoạn văn bản:
    \"\"\"{context}\"\"\"

    Định dạng đầu ra:
    - Trả về **duy nhất một danh sách Python hợp lệ**, chứa đúng {num_questions} chuỗi (string).  
    - Không thêm bất kỳ mô tả, lời giải thích hoặc ký tự thừa nào khác ngoài danh sách.  
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


# Generate answer
async def generate_answer(api_key: dict, chunks: list[str], question: str, question_language: str) -> str:
    context = "\n\n".join([f"Đoạn {i+1}: {chunk}" for i, chunk in enumerate(chunks)])
    if question_language == 'vi':
        prompt = f"""
        Bạn là một trợ lý thông minh có nhiệm vụ trả lời câu hỏi về quy định, quy chế của Trường Đại học Tôn Đức Thắng dựa trên các đoạn văn bản được cung cấp thông qua hệ thống Retrieval Augmented Generation (RAG).

        Hướng dẫn:
        1. Sử dụng **chính xác** thông tin trong các đoạn văn bản để trả lời câu hỏi một cách đầy đủ, tự nhiên, có chủ ngữ và vị ngữ rõ ràng.
        2. Nếu văn bản là **phụ lục**, cần chú ý đến cấu trúc bảng: các thông tin trong cùng một hàng thuộc về cùng một đối tượng, và cần đọc theo thứ tự từ trái sang phải để hiểu đúng ý.
        3. Nếu thông tin liên quan có trong nhiều đoạn, hãy **tổng hợp và diễn đạt lại** thành một câu trả lời hoàn chỉnh.
        4. Nếu câu trả lời có nhiều ý hoặc được liệt kê dưới dạng danh sách. Hãy thêm "\n" vào giữa các ý để tiện cho quá trình render.
        5. Nếu có đáp án, thì ở cuối câu trả lời, hãy thêm mục **Nguồn tham khảo** gồm danh sách các tài liệu đã được sử dụng (mỗi mục gồm tiêu đề và URL ở cuối đoạn văn bản).
        6. Nếu **không tìm thấy** thông tin phù hợp trong các đoạn văn bản, hãy trả lời rằng không thể tìm được tài liệu trong kho dữ liệu liên quan đến câu hỏi của người dùng, không đề cập đến các tài liệu bạn được cung cấp và không cần dẫn nguồn tham khảo.
        7. Nếu người dùng đặt câu hỏi dựa trên 1 tình huống cụ thể, hãy suy luận câu trả lời dựa trên các đoạn văn bản được cung cấp nếu như các văn bản được cung cấp có thông tin liên quan đến tình huống đó. Không được trả lời dựa trên kiến thức chung hoặc kinh nghiệm cá nhân.
        8. Nếu người dùng cố gắng trò chuyện về các chủ đề không phù hợp hoặc ngoài phạm vi thay vì hỏi về nội dung thuộc phạm vi của Trường Đại học Tôn Đức Thắng, hãy trả lời một cách lịch sự rằng bạn chỉ có thể hỗ trợ các câu hỏi liên quan đến quy định, quy chế của Trường Đại học Tôn Đức Thắng và không được thiết kế để tham gia vào các cuộc trò chuyện ngoài phạm vi này, ngoài ra không cung cấp thông tin gì thêm về tài liệu nhận được từ hệ thống RAG.
        Ngữ cảnh từ hệ thống RAG:
        {context}

        Câu hỏi:
        {question}

        Định dạng đầu ra:
        - Trả về đúng **một chuỗi (string)** chứa câu trả lời hoàn chỉnh, có thể bao gồm mục "Nguồn tham khảo:" nếu có.
        - Nếu có mục "Nguồn tham khảo", hãy liệt kê các tài liệu đã sử dụng dưới dạng danh sách, mỗi mục gồm tiêu đề, URL và không bị trùng lặp.
        """
    else:
        prompt = f"""
        You are a smart assistant tasked with answering questions about the regulations and policies of Ton Duc Thang University based on the text passages provided through the Retrieval Augmented Generation (RAG) system.

        Instructions:
        1. Use the **exact** information from the text passages to answer the question completely, naturally, with clear subject and predicate.
        2. If the text is **appendix**, pay attention to the table structure: information in the same row belongs to the same subject, and read from left to right to understand correctly.
        3. If relevant information is found in multiple passages, **synthesize and rephrase** it into a complete answer. The relevant information may be in Vietnamese, so make sure to translate your response completly to English.
        4. If the answer has multiple points or is listed as a list, add "\n" between the points for easier rendering.
        5. If there is an answer, at the end of the response, add a **References** section listing the documents used (each item includes the title and URL at the end of the passage).
        6. If **no relevant information** is found in the text passages, respond that you could not find documents related to the user's question in the database, do not mention the documents you were provided, and do not include a references section.
        7. If the user asks a question based on a specific situation, infer the answer based on the provided text passages if the provided texts contain information related to that situation. Do not answer based on general knowledge or personal experience.
        8. If the user tries to chat about inappropriate or out-of-scope topics instead of asking about the scope of Ton Duc Thang University, politely respond that you can only assist with questions related to the scope of Ton Duc Thang University and are not designed to engage in out-of-scope conversations, without providing any additional information about the documents received from the RAG system.
        9. If the question is not in Vietnamese or English, politely inform the user that you can only process questions in Vietnamese or English. This response language is the question language if you can detect it, otherwise respond in English.
        Context from RAG system:
        {context}

        Question:
        {question}

        Output format:
        - Return exactly **one string** containing the complete answer, which may include a "References:" section if applicable.
        - If there is a "References" section, list the documents used as a list, each item including the title, URL, and no duplicates.
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


# Generate general question for a cluster of questions
async def get_general_question(api_key: dict, questions: list[str]) -> str:
    prompt = f"""
    Bạn là một trợ lý thông minh có nhiệm vụ tổng hợp và tạo ra một câu hỏi chung đại diện cho một nhóm các câu hỏi liên quan đến quy định, quy chế của Trường Đại học Tôn Đức Thắng.
    
    Huớng dẫn:
    1. Đọc kỹ tất cả các câu hỏi được cung cấp.
    2. Xác định xem các câu hỏi được cung cấp có liên quan đến cùng một chủ đề hay không.
    3. Nếu các câu hỏi liên quan đến cùng một chủ đề, hãy tổng hợp thông tin từ tất cả các câu hỏi để tạo ra một câu hỏi chung bao quát ý nghĩa và phạm vi của tất cả các câu hỏi con.
    4. Nếu các câu hỏi không cùng liên quan đến một chủ đề mà có sự khác biệt rõ ràng về nội dung, trải dài trên nhiều khía cạnh khác nhau, hãy lựa chọn 1 chủ đề phổ biến nhất và tạo câu hỏi chung dựa trên chủ đề đó.
    5. Câu hỏi chung phải ngắn gọn, rõ ràng, tự nhiên và bao quát ý nghĩa của các câu hỏi con.
    6. Không được tạo ra 1 câu hỏi về quá nhiều chủ đề khác nhau.
    
    Danh sách các câu hỏi:
    {questions}
    
    Yêu cầu định dạng đầu ra:
    - Trả về đúng **một chuỗi (string)** chứa câu hỏi chung.
    - Không thêm bất kỳ mô tả, giải thích, hoặc ký tự thừa nào khác ngoài câu hỏi.
    """

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