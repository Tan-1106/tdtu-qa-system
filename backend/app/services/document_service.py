import os
import asyncio
from io import BytesIO
from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder

from app.daos import document_dao
from app.services import question_embedding_service, potential_question_service, prototype_service


UPLOAD_DIRECTORY = "uploads/documents"


# Lấy tất cả tài liệu
async def get_documents(filters: dict, skip: int, limit: int):
    docs = await document_dao.get_documents(filters=filters, skip=skip, limit=limit)
    return docs


# Lấy tài liệu theo ID
async def get_document_by_id(doc_id: str):
    doc = await document_dao.get_document_by_id(doc_id)
    if not doc:
        raise ValueError(f"Không tìm thấy tài liệu với ID {doc_id}.")
    return doc


# Lấy chunk tài liệu theo document ID và chunk index
async def get_document_chunk(doc_id: str, chunk_index: int):
    chunk = await document_dao.get_document_chunk(doc_id, chunk_index)
    if not chunk:
        raise ValueError(f"Không tìm thấy chunk {chunk_index} trong tài liệu {doc_id}.")
    return chunk


# Đếm số lượng tài liệu
async def count_documents(filters: dict):
    count = await document_dao.count_documents(filters=filters)
    return count


# Tạo tài liệu mới
async def create_document(doc_data: dict):
    doc = await document_dao.create_document(doc_data)
    return doc


# Cập nhật tài liệu hiện có
async def update_document(doc_id: str, doc_update: dict):
    updated_doc = await document_dao.update_document(doc_id, doc_update)
    return updated_doc


# Xóa tài liệu theo ID
async def delete_document(doc_id: str):
    deleted = await document_dao.delete_document(doc_id)
    if deleted:
        await question_embedding_service.delete_question_embeddings_by_doc_id(doc_id)
        await potential_question_service.delete_potential_questions_by_doc_id(doc_id)
        await prototype_service.cluster_question_embeddings()

    return deleted


# Lưu file tài liệu vào đĩa
async def save_document_file(file: UploadFile):
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)

    contents = await file.read()
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: open(file_path, "wb").write(contents)
    )
        
    return file_path


# Xem file tài liệu
async def view_document_file(doc_id: str):
    doc = await document_dao.get_document_by_id(doc_id)
    doc = jsonable_encoder(doc)
        
    file_name = doc.get("title", "document.pdf")
    file_path = doc.get("file_path", "")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError("Document file not found")
    
    loop = asyncio.get_event_loop()
    file_content = await loop.run_in_executor(
        None,
        lambda: open(file_path, "rb").read()
    )
    
    return file_name, BytesIO(file_content)
    