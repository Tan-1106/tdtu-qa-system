import os
import re
import logging
from openai import OpenAI
from app.utils import text_process
from pyvi.ViTokenizer import tokenize
from sentence_transformers import SentenceTransformer

logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

# Environment variables
GPT_KEY = os.getenv("GPT_KEY")
GPT_MODEL = os.getenv("GPT_MODEL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

gpt_client = OpenAI(api_key=GPT_KEY)
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

# Generate questions from a given text chunk
def create_questions(context: str, num_questions: int = 5) -> list[str]:
    prompt = f"""
    Bạn là một trợ lý tạo câu hỏi thông minh.

    Nhiệm vụ:
    Tạo ra {num_questions} câu hỏi **ngắn gọn**, **rõ ràng**, **không trùng lặp** và **tự nhiên**, mà một sinh viên có thể hỏi về các **quy định hoặc quy chế của trường đại học**, dựa trên **nội dung trong đoạn văn bản dưới đây**.  
    Mỗi câu hỏi phải có **ý nghĩa đầy đủ**, có thể hiểu được mà **không cần đọc lại văn bản gốc**, và **nội dung câu hỏi phải có thông tin trả lời trong đoạn văn**.

    Đoạn văn bản:
    \"\"\"{context}\"\"\"

    Yêu cầu định dạng đầu ra:
    - Trả về **một danh sách Python hợp lệ** chứa đúng {num_questions} chuỗi (string).
    - Không thêm bất kỳ mô tả, giải thích, hoặc ký tự thừa nào khác ngoài danh sách.
    - Ví dụ đầu ra:
    ["Câu hỏi 1", "Câu hỏi 2", ..., "Câu hỏi {num_questions}"]
    """

    response = gpt_client.responses.create(
        model=GPT_MODEL,
        input=prompt,
        store=False
    )

    output_text = response.output_text
    output_text = text_process.normalize_text(output_text)
    print("LOG: Generated questions:", output_text)
    return output_text

# Generate questions from a given text chunk (appendix version)
def create_questions_appendix(context: str, num_questions: int = 3) -> list[str]:
    prompt = f"""
    Bạn là một trợ lý tạo câu hỏi thông minh.

    Nhiệm vụ:
    Tạo ra {num_questions} câu hỏi **ngắn gọn**, **tự nhiên**, và **không trùng lặp** mà một sinh viên có thể hỏi về các **quy định hoặc quy chế của trường đại học**.  
    Dựa trên nội dung trong đoạn văn bản dưới đây, **chỉ sử dụng phần "Content"** để tạo câu hỏi — **không dùng phần "Description"** hoặc **"Table header"** để hình thành câu hỏi.

    Yêu cầu:
    - Câu hỏi phải **rõ nghĩa**, có thể hiểu được mà **không cần đọc lại văn bản gốc**.  
    - Chỉ tạo những câu hỏi mà **câu trả lời có thể tìm thấy** trong phần "Content" của văn bản.  
    - Không tạo câu hỏi nếu thông tin không rõ ràng hoặc không đủ dữ kiện trong nội dung.

    Đoạn văn bản:
    \"\"\"{context}\"\"\"

    Định dạng đầu ra:
    - Trả về **duy nhất một danh sách Python hợp lệ**, chứa đúng {num_questions} chuỗi (string).  
    - Không thêm bất kỳ mô tả, lời giải thích hoặc ký tự thừa nào khác ngoài danh sách.  
    - Ví dụ đầu ra:
    ["Câu hỏi 1", "Câu hỏi 2", ..., "Câu hỏi {num_questions}"]
    """



    response = gpt_client.responses.create(
        model=GPT_MODEL,
        input=prompt,
        store=False
    )

    output_text = response.output_text
    output_text = text_process.normalize_text(output_text)
    print("LOG: Generated appendix questions:", output_text)
    return output_text

# Generate answer using provided chunks and question
async def generate_answer(chunks: list[str], question: str) -> str:
    context = "\n\n".join([f"Đoạn {i+1}: {chunk}" for i, chunk in enumerate(chunks)])
    prompt = f"""
    Bạn là một trợ lý thông minh có nhiệm vụ trả lời câu hỏi dựa trên các đoạn văn bản được cung cấp.

    Hướng dẫn:
    1. Sử dụng **chính xác** thông tin trong các đoạn văn bản để trả lời câu hỏi một cách đầy đủ, tự nhiên, có chủ ngữ và vị ngữ rõ ràng.
    2. Nếu văn bản là **phụ lục**, cần chú ý đến cấu trúc bảng: các thông tin trong cùng một hàng thuộc về cùng một đối tượng, và cần đọc theo thứ tự từ trái sang phải để hiểu đúng ý.
    3. Nếu thông tin liên quan có trong nhiều đoạn, hãy **tổng hợp và diễn đạt lại** thành một câu trả lời hoàn chỉnh.
    4. Nếu có đáp án, thì ở cuối câu trả lời, hãy thêm mục **"Nguồn tham khảo:"** gồm danh sách các tài liệu đã được sử dụng (mỗi mục gồm tiêu đề và URL ở cuối đoạn văn bản).
    5. Nếu **không tìm thấy** thông tin phù hợp trong các đoạn văn bản, hãy trả lời rằng không thể tìm được tài liệu trong kho dữ liệu liên quan đến câu hỏi của người dùng và không cần dẫn nguồn tham khảo.
    6. Nếu câu hỏi không liên quan đến lĩnh vực quy định, quy chế hoặc không thuộc phạm vi của trường đại học, hãy trả lời:
    "Câu hỏi của bạn không liên quan đến quy định hoặc quy chế của trường đại học."

    Ngữ cảnh:
    {context}

    Câu hỏi:
    {question}

    Định dạng đầu ra:
    - Trả về đúng **một chuỗi (string)** chứa câu trả lời hoàn chỉnh, có thể bao gồm mục "Nguồn tham khảo:" nếu có.
    """


    response = gpt_client.responses.create(
        model=GPT_MODEL,
        input=prompt,
        store=False
    )

    answer = response.output_text.strip()
    answer = text_process.normalize_text(answer)
    return answer

# Get embedding for a given text
def get_embedding(text: str):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    
    text_tokenized = tokenize(text)
    embedding = embedding_model.encode(text_tokenized).tolist()

    return embedding