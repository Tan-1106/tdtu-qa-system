from fastapi.encoders import jsonable_encoder

from app.daos import question_dao
from app.services import model_service, prototype_service, question_embedding_service, document_service

# Get all questions
async def get_questions():
    questions = await question_dao.get_questions()
    return questions

# Get a question by ID
async def get_question_by_id(question_id: str):
    question = await question_dao.get_question_by_id(question_id)
    return question

# Create a new question
async def create_question(question: dict):
    created_question = await question_dao.create_question(question)
    return created_question

# Ask a question and get an answer
async def query(question_data: dict):
    # Get embedding for the question
    embedded_question = model_service.get_embedding(question_data['question'])

    # Semantic search for relevant prototypes
    relevant_prototypes = await prototype_service.semantic_search_prototypes(embedded_question, top_k=1)
    
    # Collect relevant question embedding IDs from prototypes
    relevant_embedding_ids = []
    for proto in jsonable_encoder(relevant_prototypes):
        metadata = proto['metadata']
        for emb_id in metadata['question_embedding_ids']:
            if emb_id not in relevant_embedding_ids:
                relevant_embedding_ids.append(emb_id)
    

    # Semantic search for relevant question embeddings
    relevant_question_embeddings = await question_embedding_service.semantic_search_question_embeddings(embedded_question, top_k=10, relevant_embedding_ids=relevant_embedding_ids)
    
    # Get chunks
    chunks = []
    for qe in jsonable_encoder(relevant_question_embeddings):
        metadata = qe['metadata']
        chunk = await document_service.get_document_chunk(metadata['doc_id'], metadata['chunk_index'])
        
        chunk = jsonable_encoder(chunk)
        chunk_content = f"""Tài liệu: {chunk['title']}. Nội dung: {chunk['chunk_text']}. URL: {chunk['file_url']}"""
        chunks.append(chunk_content)
    unique_chunks = set(chunks)
    chunks = list(unique_chunks)
    
    # Generate answer using chunks, question and LLM
    answer = await model_service.generate_answer(chunks, question_data['question'])
        
    return {
        "chunks": chunks,
        "answer": answer
    }
