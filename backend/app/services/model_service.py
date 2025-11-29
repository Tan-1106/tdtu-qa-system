import os
import re
import asyncio
import logging
from openai import OpenAI
from app.utils import text_process
from pyvi.ViTokenizer import tokenize
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer, CrossEncoder


# logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


# # --- Configuration ---
# # Biến môi trường
# GPT_KEY = os.getenv("GPT_KEY")
# GPT_5_NANO = os.getenv("GPT_5_NANO", "gpt-5-nano")
# GPT_5_MINI = os.getenv("GPT_5_MINI", "gpt-5-mini")
# EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "dangvantuan/vietnamese-embedding")
# TRANSLATE_MODEL = os.getenv("TRANSLATE_MODEL", "VietAI/envit5-translation")
# CROSS_ENCODER_MODEL = os.getenv("CROSS_ENCODER_MODEL", "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")


# # Khởi tạo client và mô hình
# gpt_client = OpenAI(api_key=GPT_KEY)
# embedding_model = SentenceTransformer(EMBEDDING_MODEL)
# translate_tokenizer = AutoTokenizer.from_pretrained(TRANSLATE_MODEL)
# translate_model = AutoModelForSeq2SeqLM.from_pretrained(TRANSLATE_MODEL)
# cross_encoder_model = CrossEncoder(CROSS_ENCODER_MODEL)


# # --- Service Functions ---
# # Tạo bộ câu hỏi tiềm năng từ đoạn văn bản với prompt và LLM
# def create_questions(context: str, num_questions: int = 5) -> list[str]:
#     # Tạo prompt
#     prompt = f"""
#     Bạn là một trợ lý tạo câu hỏi thông minh.

#     Nhiệm vụ:
#     Sinh ra đúng {num_questions} câu hỏi tiềm năng đáp ứng toàn bộ tiêu chí sau:
#     - Ngắn gọn, rõ ràng, không trùng lặp, tự nhiên.
#     - Là những câu hỏi mà một sinh viên tại Trường Đại học Tôn Đức Thắng có thể đặt ra liên quan đến phạm vi, hoạt động, quy định… của trường dựa trên đoạn văn bạn được cung cấp bên dưới bằng hệ thống Retrieval-Augmented Generation (RAG).
#     - Không được hỏi dựa theo cú pháp hoặc câu chữ cụ thể trong văn bản, chỉ dựa trên chủ đề có thể được văn bản đề cập.
#     - Không được nhắc đến bản thân văn bản hoặc vị trí văn bản (ví dụ: “theo văn bản trên”, “dựa trên nội dung đã cho”, “thông báo này”, “quy định này”,...).
#     - Câu hỏi phải có ý nghĩa đầy đủ, người đọc không cần xem đoạn văn bản vẫn hiểu được.
#     - Ít nhất phải có 1 câu hỏi tổng quát về chủ đề chính của đoạn văn bản.
#     Đoạn văn bản:
#     \"\"\"{context}\"\"\"

#     Yêu cầu định dạng đầu ra:
#     - Trả về **một danh sách Python hợp lệ** chứa đúng {num_questions} chuỗi (string).
#     - Không thêm bất kỳ mô tả, giải thích, hoặc ký tự thừa nào khác ngoài danh sách.
#     - Ví dụ đầu ra:
#     ["Câu hỏi 1", "Câu hỏi 2", ..., "Câu hỏi {num_questions}"]
#     """

#     response = gpt_client.responses.create(
#         model=GPT_5_NANO,
#         input=prompt,
#         store=False
#     )

#     output_text = response.output_text
#     output_text = text_process.normalize_text(output_text)
    
#     # Logging
#     print("- LOG: Generated questions for context:")
#     print(context)
#     for i in output_text:
#         print(f"  - {i}")
    
#     return output_text


# # Tạo bộ câu hỏi tiềm năng từ đoạn văn bản phụ lục với prompt và LLM
# def create_questions_appendix(context: str, num_questions: int = 3) -> list[str]:
#     # Tạo prompt
#     prompt = f"""
#     Bạn là một trợ lý tạo câu hỏi tiềm năng dựa trên nội dung phụ lục quy định được cung cấp.
    
#     Nhiệm vụ:
#     Sinh ra đúng {num_questions} câu hỏi tiềm năng đáp ứng toàn bộ tiêu chí sau:
#     - Ngắn gọn, rõ ràng, không trùng lặp, tự nhiên.
#     - Là những câu hỏi mà một sinh viên tại Trường Đại học Tôn Đức Thắng có thể đặt ra liên quan đến quy định, quy chế của trường dựa trên đoạn văn bạn được cung cấp bên dưới bằng hệ thống Retrieval-Augmented Generation (RAG).
#     - Không được hỏi dựa theo cú pháp hoặc câu chữ cụ thể trong văn bản, chỉ dựa trên chủ đề có thể được văn bản đề cập.
#     - Không được nhắc đến bản thân văn bản hoặc vị trí văn bản (ví dụ: "Theo Description", "theo Content", “dựa trên nội dung đã cho”, “quy định này”,...).
#     - Câu hỏi phải có ý nghĩa đầy đủ, người đọc không cần xem đoạn văn bản vẫn hiểu được.
#     - Chỉ tạo những câu hỏi trong phạm vi mà phần "Content" của phụ lục đang đề cập đến.
    
#     Đoạn văn bản:
#     \"\"\"{context}\"\"\"

#     Định dạng đầu ra:
#     - Trả về **duy nhất một danh sách Python hợp lệ**, chứa đúng {num_questions} chuỗi (string).  
#     - Không thêm bất kỳ mô tả, lời giải thích hoặc ký tự thừa nào khác ngoài danh sách.  
#     - Ví dụ đầu ra:
#     ["Câu hỏi 1", "Câu hỏi 2", ..., "Câu hỏi {num_questions}"]
#     """

#     response = gpt_client.responses.create(
#         model=GPT_5_NANO,
#         input=prompt,
#         store=False
#     )

#     output_text = response.output_text
#     output_text = text_process.normalize_text(output_text)
    
#     print("- LOG: Generated appendix questions for context:")
#     print(context)
#     for i in output_text:
#         print(f"  - {i}")
        
#     return output_text


# # Tạo câu trả lời cho câu hỏi dựa trên các đoạn văn bản liên quan
# async def generate_answer(chunks: list[str], question: str, lang: str) -> str:
#     # Tạo prompt
#     context = "\n\n".join([f"Đoạn {i+1}: {chunk}" for i, chunk in enumerate(chunks)])
#     if lang == 'vi':
#         prompt = f"""
#         Bạn là một trợ lý thông minh có nhiệm vụ trả lời câu hỏi về quy định, quy chế của Trường Đại học Tôn Đức Thắng dựa trên các đoạn văn bản được cung cấp thông qua hệ thống Retrieval Augmented Generation (RAG).

#         Hướng dẫn:
#         1. Sử dụng **chính xác** thông tin trong các đoạn văn bản để trả lời câu hỏi một cách đầy đủ, tự nhiên, có chủ ngữ và vị ngữ rõ ràng.
#         2. Nếu văn bản là **phụ lục**, cần chú ý đến cấu trúc bảng: các thông tin trong cùng một hàng thuộc về cùng một đối tượng, và cần đọc theo thứ tự từ trái sang phải để hiểu đúng ý.
#         3. Nếu thông tin liên quan có trong nhiều đoạn, hãy **tổng hợp và diễn đạt lại** thành một câu trả lời hoàn chỉnh.
#         4. Nếu có đáp án, thì ở cuối câu trả lời, hãy thêm mục **Nguồn tham khảo** gồm danh sách các tài liệu đã được sử dụng (mỗi mục gồm tiêu đề và URL ở cuối đoạn văn bản).
#         5. Nếu **không tìm thấy** thông tin phù hợp trong các đoạn văn bản, hãy trả lời rằng không thể tìm được tài liệu trong kho dữ liệu liên quan đến câu hỏi của người dùng, không đề cập đến các tài liệu bạn được cung cấp và không cần dẫn nguồn tham khảo.
#         6. Nếu người dùng cố gắng trò chuyện về các chủ đề không phù hợp hoặc ngoài phạm vi thay vì hỏi về nội dung thuộc phạm vi của Trường Đại học Tôn Đức Thắng, hãy trả lời một cách lịch sự rằng bạn chỉ có thể hỗ trợ các câu hỏi liên quan đến quy định, quy chế của Trường Đại học Tôn Đức Thắng và không được thiết kế để tham gia vào các cuộc trò chuyện ngoài phạm vi này, ngoài ra không cung cấp thông tin gì thêm về tài liệu nhận được từ hệ thống RAG.

#         Ngữ cảnh từ hệ thống RAG:
#         {context}

#         Câu hỏi:
#         {question}

#         Định dạng đầu ra:
#         - Trả về đúng **một chuỗi (string)** chứa câu trả lời hoàn chỉnh, có thể bao gồm mục "Nguồn tham khảo:" nếu có.
#         """
#     else:
#         prompt = f"""
#         You are a smart assistant tasked with answering questions about the regulations and policies of Ton Duc Thang University based on the text passages provided through the Retrieval Augmented Generation (RAG) system.

#         Instructions:
#         1. Use the **exact** information from the text passages to answer the question completely, naturally, with clear subject and predicate.
#         2. If the text is **appendix**, pay attention to the table structure: information in the same row belongs to the same subject, and read from left to right to understand correctly.
#         3. If relevant information is found in multiple passages, **synthesize and rephrase** it into a complete answer. The relevant information may be in Vietnamese, so make sure to translate your response completly to English.
#         4. If there is an answer, at the end of the response, add a **References** section listing the documents used (each item includes the title and URL at the end of the passage).
#         5. If **no relevant information** is found in the text passages, respond that you could not find documents related to the user's question in the database, do not mention the documents you were provided, and do not include a references section.
#         6. If the user tries to chat about inappropriate or out-of-scope topics instead of asking about the scope of Ton Duc Thang University, politely respond that you can only assist with questions related to the scope of Ton Duc Thang University and are not designed to engage in out-of-scope conversations, without providing any additional information about the documents received from the RAG system.
#         7. If the question is not in Vietnamese or English, politely inform the user that you can only process questions in Vietnamese or English. This response language is the question language if you can detect it, otherwise respond in English.

#         Context from RAG system:
#         {context}

#         Question:
#         {question}

#         Output format:
#         - Return exactly **one string** containing the complete answer, which may include a "References:" section if applicable.
#         """
        
#     response = gpt_client.responses.create(
#         model=GPT_5_MINI,
#         input=prompt,
#         store=False
#     )

#     answer = response.output_text.strip()
#     answer = text_process.normalize_text(answer)
    
#     return answer


# # Lấy embedding của văn bản
# def get_embedding(text: str):
#     text = text.strip()
#     text = re.sub(r'\s+', ' ', text)
    
#     text_tokenized = tokenize(text)
#     embedding = embedding_model.encode(text_tokenized).tolist()

#     return embedding


# # Dịch văn bản từ tiếng Anh sang tiếng Việt
# async def translate_to_vietnamese(text: str) -> str:
#     loop = asyncio.get_event_loop()
    
#     def _translate():
#         input_text = ["en: " + text]
        
#         inputs = translate_tokenizer(input_text, return_tensors="pt", padding=True)
#         output = translate_model.generate(
#             inputs.input_ids,
#             max_length=512,
#             num_beams=5,
#             early_stopping=True
#         )
#         translated = translate_tokenizer.batch_decode(output, skip_special_tokens=True)
        
#         return translated[0]
    
#     result = await loop.run_in_executor(None, _translate)
#     return result


# # Rerank các đoạn văn bản dựa trên điểm số từ Cross-Encoder và lấy top_k đoạn
# def rerank_chunks(question: str, chunks: list[str], top_k: int = 5) -> list[str]:
#     scored_chunks = {}
#     for chunk in chunks:
#         score = cross_encoder_model.predict([[question, chunk]])[0]
#         scored_chunks[chunk] = float(score)
    
#     sorted_scored_chunks = sorted(scored_chunks, key=scored_chunks.get, reverse=True)
#     top_chunks = sorted_scored_chunks[:top_k]
    
#     # Logging
#     print("- LOG: Reranked chunks:")
#     for i, chunk in enumerate(top_chunks):
#         print(f"  {i+1}. (score: {scored_chunks[chunk]:.4f}) {chunk}")
    
#     return top_chunks