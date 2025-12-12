# User
def user_serialize(user) -> dict:
    return {
        "id": str(user["_id"]),
        "sub": str(user["sub"]),
        "name": user.get("name"),
        "email": user.get("email"),
        "image": user.get("image"),
        "role": user.get("role"),
        "faculty": user.get("faculty"),
        "is_faculty_manager": user.get("is_faculty_manager", False),
        "system_role_assigned": user.get("system_role_assigned", False),
        "banned": user.get("banned", False),
        "created_at": user.get("created_at").isoformat() if user.get("created_at") else None
    }
    

# Tokens
def tokens_serialize(tokens) -> dict:
    return {
        "access_token": tokens.get("access_token"),
        "refresh_token": tokens.get("refresh_token"),
        "revoked": tokens.get("revoked", False),
        "created_at": tokens.get("created_at").isoformat() if tokens.get("created_at") else None,
        "revoked_at": tokens.get("revoked_at").isoformat() if tokens.get("revoked_at") else None
    }
    

# API Key
def api_key_serialize(api_key) -> dict:
    return {
        "id": str(api_key["_id"]),
        "name": api_key.get("name"),
        "description": api_key.get("description"),
        "api_key": api_key.get("api_key"),
        "provider": api_key.get("provider"),
        "is_using": api_key.get("is_using", False),
        "using_model": api_key.get("using_model"),
        "created_at": api_key.get("created_at").isoformat() if api_key.get("created_at") else None,
        "updated_at": api_key.get("updated_at").isoformat() if api_key.get("updated_at") else None
    }
    
    
# Document
def document_serialize(document) -> dict:
    return {
        "id": str(document["_id"]),
        "file_name": document.get("file_name"),
        "doc_type": document.get("doc_type"),
        "department": document.get("department"),
        "faculty": document.get("faculty"),
        "file_url": document.get("file_url"),
        "file_path": document.get("file_path"),
        "uploaded_by": document.get("uploaded_by"),
        "uploaded_at": document.get("uploaded_at").isoformat() if document.get("uploaded_at") else None,
        "updated_by": document.get("updated_by"),
        "updated_at": document.get("updated_at").isoformat() if document.get("updated_at") else None
    }
    
    
# Document Chunk
def document_chunk_serialize(document_chunk) -> dict:
    return {
        "id": str(document_chunk["_id"]),
        "doc_id": str(document_chunk.get("doc_id")),
        "chunks": document_chunk.get("chunks", {}),
        "created_at": document_chunk.get("created_at").isoformat() if document_chunk.get("created_at") else None,
        "updated_at": document_chunk.get("updated_at").isoformat() if document_chunk.get("updated_at") else None
    }
    
    
# QA Session
def qa_session_serialize(qa_session) -> dict:
    return {
        "id": str(qa_session["_id"]),
        "user_id": qa_session.get("user_id"),
        "user_sub": qa_session.get("user_sub"),
        "user_faculty": qa_session.get("user_faculty"),
        "question": qa_session.get("question"),
        "answer": qa_session.get("answer"),
        "feedback": qa_session.get("feedback"),
        "manager_answer": qa_session.get("manager_answer"),
        "start_date": qa_session.get("start_date").isoformat() if qa_session.get("start_date") else None,
        "end_date": qa_session.get("end_date").isoformat() if qa_session.get("end_date") else None,
        "created_at": qa_session.get("created_at").isoformat() if qa_session.get("created_at") else None,
        "updated_at": qa_session.get("updated_at").isoformat() if qa_session.get("updated_at") else None
    }
    
    
# Popular Question Statistics
def popular_question_statistics_serialize(statistics) -> dict:
    return {
        "id": str(statistics["_id"]),
        "question": statistics.get("question"),
        "answer": statistics.get("answer"),
        "summary": statistics.get("summary", {}),
        "is_display": statistics.get("is_display", False),
        "created_at": statistics.get("created_at").isoformat() if statistics.get("created_at") else None,
        "updated_at": statistics.get("updated_at").isoformat() if statistics.get("updated_at") else None
    }