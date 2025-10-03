# Document
def document_serialize(doc) -> dict:
    return {
        "id": str(doc["_id"]),
        "title": doc.get("title"),
        "chunks": doc.get("chunks", []),
        "doc_type": doc.get("doc_type"),
        "tags": doc.get("tags", []),
        "language": doc.get("language"),
        "file_url": doc.get("file_url"),
        "uploaded_by": doc.get("uploaded_by"),
        "edited_by": doc.get("edited_by"),     
        "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
        "updated_at": doc.get("updated_at").isoformat() if doc.get("updated_at") else None,
    }
