import os
import re
from openai import OpenAI
from app.utils import text_process
from pyvi.ViTokenizer import tokenize
from sentence_transformers import SentenceTransformer

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
        Nhiệm vụ: tạo ra {num_questions} câu hỏi ngắn gọn, tự nhiên mà một sinh viên có thể hỏi về các quy định hoặc quy chế của trường đại học, 
        dựa trên nội dung trong đoạn văn bản sau đây. 
        Chỉ tạo những câu hỏi mà thông tin trả lời có thể tìm thấy trong đoạn văn.

        Đoạn văn bản:
        \"\"\"{context}\"\"\"

        Yêu cầu định dạng đầu ra:
        Trả về đúng một danh sách Python hợp lệ chứa {num_questions} chuỗi (string), không thêm bất kỳ nội dung nào khác.
        Ví dụ:
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
        Nhiệm vụ: tạo ra {num_questions} câu hỏi ngắn gọn, tự nhiên mà một sinh viên có thể hỏi về các quy định hoặc quy chế của trường đại học. 
        Dựa trên nội dung trong đoạn văn bản sau đây, chỉ tạo câu hỏi dựa trên nội dung "Content" của văn bản, không tạo dựa trên "Description" và "Table header".
        Câu hỏi được tạo ra phải rõ nghĩa và không cần phải đối chiếu tài liệu văn bản để hiểu ý nghĩa của câu hỏi.
        Chỉ tạo những câu hỏi mà thông tin trả lời có thể tìm thấy trong đoạn văn.

        Đoạn văn bản:
        \"\"\"{context}\"\"\"

        Yêu cầu định dạng đầu ra:
        Trả về đúng một danh sách Python hợp lệ chứa {num_questions} chuỗi (string), không thêm bất kỳ nội dung nào khác.
        Ví dụ:
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

# Get embedding for a given text
def get_embedding(text: str):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    
    text_tokenized = tokenize(text)
    embedding = embedding_model.encode(text_tokenized).tolist()

    return embedding

# Generate answer using provided chunks and question
async def generate_answer(chunks: list[str], question: str) -> str:
    context = "\n\n".join([f"Đoạn {i+1}: {chunk}" for i, chunk in enumerate(chunks)])
    prompt = f"""
        Bạn là một trợ lý thông minh giúp trả lời các câu hỏi dựa trên ngữ cảnh được cung cấp.
        Nhiệm vụ: sử dụng thông tin từ các đoạn văn bản dưới đây để trả lời câu hỏi một cách chính xác, đầy đủ, tự nhiên và giải thích chi tiết dựa trên tài liệu nếu cần thiết.
        Nếu văn bản được cung cấp là phụ lục, cần chú ý cấu trúc bảng để tìm thông tin chính xác theo thứ tự của các ô trong 1 dòng.
        Nếu thông tin có trong các đoạn văn bản, khi trả lời xong thì dẫn nguồn theo định dạng: ". Theo văn bản [Document Title] - [File URL]", nếu có nhiều nguồn thì liệt kê tất cả.
        Nếu thông tin không có trong các đoạn văn, hãy trả lời "Không tìm thấy tài liệu liên quan đến câu hỏi của bạn."

        Ngữ cảnh:
        {context}

        Câu hỏi:
        {question}

        Yêu cầu định dạng đầu ra:
        Trả về đúng một chuỗi (string) chứa câu trả lời đầy đủ từ đoạn văn bản có ngữ cảnh. Câu trả lời phải rõ ràng, mạch lạc, dễ hiểu và đầy đủ chủ ngữ, vị ngữ.
    """

    response = gpt_client.responses.create(
        model=GPT_MODEL,
        input=prompt,
        store=False
    )

    answer = response.output_text.strip()
    answer = text_process.normalize_text(answer)
    return answer