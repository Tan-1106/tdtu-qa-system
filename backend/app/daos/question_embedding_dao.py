import json
import uuid
from fastapi.encoders import jsonable_encoder

from app.databases import chroma
from app.schemas import question_embedding_schema


# Lấy tất cả các embedding câu hỏi
async def get_question_embeddings() -> list[question_embedding_schema.QuestionEmbeddingResponse]:
    results = chroma.question_embeddings_collection.get(include=["embeddings", "metadatas"])
    if not results or 'ids' not in results:
        return []
    
    embeddings = []
    for idx in range(len(results['ids'])):
        embeddings.append(
            question_embedding_schema.QuestionEmbeddingResponse(
                id=results['ids'][idx],
                vector=results['embeddings'][idx],
                metadata=results['metadatas'][idx]
            )
        )
    return embeddings


# Lấy một embedding câu hỏi theo ID
async def get_question_embedding_by_id(embedding_id: str) -> question_embedding_schema.QuestionEmbeddingResponse:
    results = chroma.question_embeddings_collection.get(ids=[embedding_id], include=["embeddings", "metadatas"])
    if not results or 'ids' not in results or len(results['ids']) == 0:
        raise ValueError("Không tìm thấy embedding câu hỏi.")
    
    return question_embedding_schema.QuestionEmbeddingResponse(
        id=results['ids'][0],
        vector=results['embeddings'][0],
        metadata=results['metadatas'][0]
    )


# Tạo một embedding câu hỏi mới
async def create_question_embedding(embedding: question_embedding_schema.QuestionEmbeddingCreate) -> question_embedding_schema.QuestionEmbeddingResponse:
    embedding = jsonable_encoder(embedding)
    embedding_id = str(uuid.uuid4())
    
    chroma.question_embeddings_collection.add(
        ids=[embedding_id],
        embeddings=[embedding["vector"]],
        metadatas=[embedding["metadata"]],
    )
    
    return question_embedding_schema.QuestionEmbeddingResponse(
        id=embedding_id,
        vector=embedding["vector"],
        metadata=embedding["metadata"]
    )
    
    
# Nhập embedding câu hỏi từ file JSON
async def import_question_embeddings_file(file):
    content = await file.read()
    data = json.loads(content)

    imported_embeddings = []
    for item in data:
        embedding_create = jsonable_encoder(question_embedding_schema.QuestionEmbeddingImport(
            id=item["id"],
            vector=item["vector"],
            metadata={
                "doc_id": item["metadata"]["doc_id"],
                "chunk_index": item["metadata"]["chunk_index"]
            }
        ))
        chroma.question_embeddings_collection.add(
            ids=[embedding_create["id"]],
            embeddings=[embedding_create["vector"]],
            metadatas=[embedding_create["metadata"]]
        )
        imported_embeddings.append(embedding_create)
    
    return imported_embeddings
    
    
# Cập nhật một embedding câu hỏi theo ID
async def update_question_embedding(embedding_id: str, embedding_update: question_embedding_schema.QuestionEmbeddingCreate) -> question_embedding_schema.QuestionEmbeddingResponse:
    updated_data = jsonable_encoder(embedding_update)
    
    # Xóa embedding cũ
    chroma.question_embeddings_collection.delete(ids=[embedding_id])
    
    # Thêm embedding đã cập nhật
    chroma.question_embeddings_collection.add(
        ids=[embedding_id],
        embeddings=[updated_data["vector"]],
        metadatas=[updated_data["metadata"]]
    )
    
    return question_embedding_schema.QuestionEmbeddingResponse(
        id=embedding_id,
        vector=updated_data["vector"],
        metadata=updated_data["metadata"]
    )


# Xóa một embedding câu hỏi theo ID
async def delete_question_embedding(embedding_id: str) -> bool:
    try:
        chroma.question_embeddings_collection.delete(ids=[embedding_id])
        return True
    
    except ValueError as e:
        raise ValueError("Không tìm thấy embedding câu hỏi: " + str(e))
    except Exception as e:
        raise Exception("Lỗi khi xóa embedding câu hỏi: " + str(e))
    
    
# Xóa các embedding câu hỏi theo ID tài liệu
async def delete_question_embeddings_by_doc_id(doc_id: str) -> bool:
    try:
        chroma.question_embeddings_collection.delete(
            where={"doc_id": doc_id}
        )
        return True
    except Exception as e:
        raise Exception("Lỗi khi xóa các embedding câu hỏi cho ID tài liệu " + doc_id + ": " + str(e))
    
    
# Đặt lại (reset) collection question_embeddings
async def reset_question_embeddings_collection() -> bool:
    try:
        chroma.client.delete_collection("question_embeddings")
        chroma.question_embeddings_collection = chroma.client.create_collection("question_embeddings")
        return True
    except Exception as e:
        raise Exception("Lỗi khi xóa tất cả các embedding câu hỏi: " + str(e))
    
    
# Tìm kiếm ngữ nghĩa embedding câu hỏi
async def semantic_search_question_embeddings(
    query_vector: list[float],
    top_k: int,
    relevant_embedding_ids: list[str] = None
) -> list[question_embedding_schema.QuestionEmbeddingResponse]:    
    if relevant_embedding_ids:
        temp_name = f"temp_search_{uuid.uuid4().hex[:8]}"
        sub_collection = chroma.client.create_collection(name=temp_name)
        try:
            data = chroma.question_embeddings_collection.get(
                ids=relevant_embedding_ids,
                include=["embeddings", "metadatas"]
            )
            if not data or 'ids' not in data or len(data['ids']) == 0:
                return []

            sub_collection.add(
                ids=data['ids'],
                embeddings=data['embeddings'],
                metadatas=data['metadatas']
            )

            results = sub_collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                include=["embeddings", "metadatas"]
            )
        finally:
            chroma.client.delete_collection(temp_name)
    else:
        results = chroma.question_embeddings_collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["embeddings", "metadatas"]
        )

    if not results or 'ids' not in results or len(results['ids']) == 0:
        return []

    ids = results["ids"][0]
    embeddings = results["embeddings"][0]
    metadatas = results["metadatas"][0]
    return [
        question_embedding_schema.QuestionEmbeddingResponse(
            id=ids[i],
            vector=embeddings[i],
            metadata=metadatas[i]
        )
        for i in range(len(ids))
    ]