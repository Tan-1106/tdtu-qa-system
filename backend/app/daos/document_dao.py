import os
from typing import List
from bson import ObjectId
from datetime import datetime, timezone

from app.databases import mongo
from app.utils import serializer
from app.schemas import document_schema


# # Lấy tất cả các tài liệu
# async def get_documents(filters: dict, skip: int, limit: int) -> List[document_schema.DocumentResponse]:
#     docs = []
#     async for doc in mongo.get_documents_collection().find(filters).skip(skip).limit(limit):
#         docs.append(document_schema.DocumentResponse(**serializer.document_serialize(doc)))
#     return docs


# # Lấy một tài liệu theo ID
# async def get_document_by_id(doc_id: str) -> document_schema.DocumentResponse:
#     doc = await mongo.get_documents_collection().find_one({"_id": ObjectId(doc_id)})
#     if not doc:
#         raise ValueError("Không tìm thấy tài liệu")
#     return document_schema.DocumentResponse(**serializer.document_serialize(doc))


# # Lấy một đoạn văn bản của tài liệu theo document ID và chunk index
# async def get_document_chunk(doc_id: str, chunk_index: int) -> document_schema.DocumentChunkResponse:
#     if not ObjectId.is_valid(doc_id):
#         raise ValueError("ID tài liệu không hợp lệ")
    
#     doc = await mongo.get_documents_collection().find_one({"_id": ObjectId(doc_id)})
#     if not doc:
#         raise ValueError("Không tìm thấy tài liệu")    
#     doc = serializer.document_serialize(doc)

#     chunks = doc.get("chunks", [])
#     if chunk_index < 0 or chunk_index >= len(chunks):
#         raise ValueError("Index đoạn văn bản không hợp lệ")
    
#     chunk = chunks[chunk_index]
#     return document_schema.DocumentChunkResponse(
#         doc_id=doc_id,
#         title=doc.get("title", ""),
#         chunk_index=chunk_index,
#         chunk_text=chunk,
#         file_url=doc.get("file_url", "")
#     )


# # Lấy số lượng tài liệu
# async def count_documents(filters: dict) -> int:
#     count = await mongo.get_documents_collection().count_documents(filters)
#     return count


# # Tạo một tài liệu mới
# async def create_document(doc: dict) -> document_schema.DocumentResponse:
#     doc["created_at"] = datetime.now(timezone.utc)
#     result = await mongo.get_documents_collection().insert_one(doc)
    
#     created_doc = await mongo.get_documents_collection().find_one({"_id": result.inserted_id})
#     return document_schema.DocumentResponse(**serializer.document_serialize(created_doc))


# # Cập nhật một tài liệu
# async def update_document(doc_id: str, doc_update: dict) -> document_schema.DocumentResponse:
#     if not ObjectId.is_valid(doc_id):
#         raise ValueError("ID tài liệu không hợp lệ")
    
#     doc_update["updated_at"] = datetime.now(timezone.utc)
#     result = await mongo.get_documents_collection().update_one(
#         {"_id": ObjectId(doc_id)},
#         {"$set": doc_update}
#     )
#     if result.matched_count == 0:
#         raise ValueError("Không tìm thấy tài liệu")
    
#     updated_doc = await mongo.get_documents_collection().find_one({"_id": ObjectId(doc_id)})
#     return document_schema.DocumentResponse(**serializer.document_serialize(updated_doc))


# # Xóa một tài liệu theo ID
# async def delete_document(doc_id: str) -> bool:
#     if not ObjectId.is_valid(doc_id):
#         raise ValueError("ID tài liệu không hợp lệ")

#     doc = await mongo.get_documents_collection().find_one({"_id": ObjectId(doc_id)})
#     file_path = doc.get("file_path") if doc else None
#     if file_path and os.path.exists(file_path):
#         os.remove(file_path)        

#     result = await mongo.get_documents_collection().delete_one({"_id": ObjectId(doc_id)})

#     if result.deleted_count == 0:
#         raise ValueError("Không tìm thấy tài liệu")
    
#     return result.deleted_count > 0