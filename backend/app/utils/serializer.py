# User
def user_serialize(user) -> dict:
    return {
        "id": str(user["_id"]),
        "full_name": user.get("full_name"),
        "username": user.get("username"),
        "email": user.get("email"),
        "password": user.get("password"),
        "role": user.get("role"),
        "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
        "updated_at": user.get("updated_at").isoformat() if user.get("updated_at") else None,
    }

# Document
def document_serialize(doc) -> dict:
    return {
        "id": str(doc["_id"]),
        "uploaded_file_id": str(doc.get("uploaded_file_id")),
        "title": doc.get("title"),
        "chunks": doc.get("chunks", []),
        "doc_type": doc.get("doc_type"),
        "department": doc.get("department"),
        "language": doc.get("language"),
        "file_url": doc.get("file_url"),
        "uploaded_by": doc.get("uploaded_by"),
        "edited_by": doc.get("edited_by"),     
        "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
        "updated_at": doc.get("updated_at").isoformat() if doc.get("updated_at") else None,
    }
    
# Document Chunk
def document_chunk_serialize(chunk) -> dict:
    return {
        "doc_id": str(chunk.get("doc_id")),
        "chunk_index": chunk.get("chunk_index"),
        "chunk_text": chunk.get("chunk_text"),
    }
    
# Question
def question_serialize(question) -> dict:
    return {
        "id": str(question["_id"]),
        "user_id": question.get("user_id"),
        "question": question.get("question"),
        "status": question.get("status"),
        "answer_id": question.get("answer_id"),
        "created_at": question.get("created_at").isoformat() if question.get("created_at") else None,
    }
