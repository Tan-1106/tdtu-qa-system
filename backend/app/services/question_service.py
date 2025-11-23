from fastapi.encoders import jsonable_encoder

from app.daos import question_dao
from app.services import model_service, prototype_service, question_embedding_service, document_service


# Lấy tất cả các câu hỏi
async def get_questions():
    questions = await question_dao.get_questions()
    return questions


# Lấy một câu hỏi theo ID
async def get_question_by_id(question_id: str):
    question = await question_dao.get_question_by_id(question_id)
    return question


# Tạo một câu hỏi mới
async def create_question(question: dict):
    created_question = await question_dao.create_question(question)
    return created_question


# Hỏi một câu hỏi và nhận câu trả lời
async def query(question_data: dict, lang: str = 'vi'):
    # Lấy embedding cho câu hỏi
    if lang == 'en':
        embedded_question = model_service.get_embedding(question_data['translated_question'])
    else:
        embedded_question = model_service.get_embedding(question_data['question'])

    # Tìm kiếm ngữ nghĩa cho prototypes liên quan
    relevant_prototypes = await prototype_service.semantic_search_prototypes(embedded_question, top_k=3)
    
    # Thu thập các ID embedding câu hỏi tiềm năng liên quan từ prototypes
    relevant_embedding_ids = []
    for proto in jsonable_encoder(relevant_prototypes):
        metadata = proto['metadata']
        for emb_id in metadata['question_embedding_ids']:
            if emb_id not in relevant_embedding_ids:
                relevant_embedding_ids.append(emb_id)
    

    # Tìm kiếm ngữ nghĩa cho các embedding câu hỏi tiềm năng liên quan
    relevant_question_embeddings = await question_embedding_service.semantic_search_question_embeddings(embedded_question, top_k=30, relevant_embedding_ids=relevant_embedding_ids)
    
    # Lấy các đoạn văn bản
    chunks = []
    for qe in jsonable_encoder(relevant_question_embeddings):
        metadata = qe['metadata']
        chunk = await document_service.get_document_chunk(metadata['doc_id'], metadata['chunk_index'])
        
        chunk = jsonable_encoder(chunk)
        chunk_content = f"""Tài liệu: {chunk['title']}. Nội dung: {chunk['chunk_text']}. URL: {chunk['file_url']}"""
        chunks.append(chunk_content)
    unique_chunks = set(chunks)
    chunks = list(unique_chunks)
    chunks = model_service.rerank_chunks(question_data['question'], chunks, top_k=10)
    
    # Tạo câu trả lời sử dụng các đoạn văn bản, câu hỏi và LLM
    answer = await model_service.generate_answer(chunks, question_data['question'], lang)
    return answer[0]


# Cập nhật trạng thái câu hỏi với câu trả lời
async def update_question_status(question_id: str, answer: str, status: str = "Answered"):
    updated_question = await question_dao.update_question_status(question_id, answer, status)
    return updated_question


# Để lại phản hồi cho một câu hỏi
async def leave_feedback(question_id: str, user_id: str, feedback: str):
    question = await question_dao.get_question_by_id(question_id)
    if not question:
        raise ValueError("Question not found.")
    
    question = jsonable_encoder(question)
    if question['user_id'] != user_id:
        raise PermissionError("Người dùng không được phép để lại phản hồi cho câu hỏi này.")
    
    # Cập nhật phản hồi
    updated_question = await question_dao.update_question_feedback(question_id, feedback)
    return updated_question