import os
import torch
from openai import OpenAI
from app.utils import text_process
from pyvi.ViTokenizer import tokenize
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoTokenizer

# Environment variables
GPT_KEY = os.getenv("GPT_KEY")
GPT_MODEL = os.getenv("GPT_MODEL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

device = "cuda" if torch.cuda.is_available() else "cpu"
gpt_client = OpenAI(api_key=GPT_KEY)
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

# Generate questions from a given text chunk
def create_questions(context: str):
    prompt = f"""
        Bạn là một trợ lý tạo câu hỏi thông minh.
        Nhiệm vụ: tạo ra 10 câu hỏi ngắn gọn, tự nhiên mà một sinh viên có thể hỏi về các quy định hoặc quy chế của trường đại học, 
        dựa trên nội dung trong đoạn văn bản sau đây. 
        Chỉ tạo những câu hỏi mà thông tin trả lời có thể tìm thấy trong đoạn văn.

        Đoạn văn bản:
        \"\"\"{context}\"\"\"

        Yêu cầu định dạng đầu ra:
        Trả về đúng một danh sách Python hợp lệ chứa 10 chuỗi (string), không thêm bất kỳ nội dung nào khác.
        Ví dụ:
        ["Câu hỏi 1", "Câu hỏi 2", "Câu hỏi 3", ..., "Câu hỏi 10"]
    """


    response = gpt_client.responses.create(
        model=GPT_MODEL,
        input=prompt,
        store=False
    )

    output_text = response.output_text
    output_text = text_process.normalize_text(output_text)
    return output_text

# Get embedding for a given text
def get_embedding(text: str):
    text_tokenized = tokenize(text)
    embedding = embedding_model.encode(text_tokenized).tolist()

    return embedding