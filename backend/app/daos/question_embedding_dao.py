import uuid
from fastapi.encoders import jsonable_encoder

from app.databases import chroma
from app.schemas import question_embedding_schema

# Read all question embeddings
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

# Read a question embedding by ID
async def get_question_embedding_by_id(embedding_id: str) -> question_embedding_schema.QuestionEmbeddingResponse:
    results = chroma.question_embeddings_collection.get(ids=[embedding_id], include=["embeddings", "metadatas"])
    if not results or 'ids' not in results or len(results['ids']) == 0:
        raise ValueError("Question embedding not found.")
    
    return question_embedding_schema.QuestionEmbeddingResponse(
        id=results['ids'][0],
        vector=results['embeddings'][0],
        metadata=results['metadatas'][0]
    )

# Create a new question embedding
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
    
# Update a question embedding by ID
async def update_question_embedding(embedding_id: str, embedding_update: question_embedding_schema.QuestionEmbeddingCreate) -> question_embedding_schema.QuestionEmbeddingResponse:
    updated_data = jsonable_encoder(embedding_update)
    
    # Delete the old embedding
    chroma.question_embeddings_collection.delete(ids=[embedding_id])
    
    # Add the updated embedding
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

# Delete a question embedding by ID
async def delete_question_embedding(embedding_id: str) -> bool:
    try:
        chroma.question_embeddings_collection.delete(ids=[embedding_id])
        return True
    
    except ValueError as e:
        raise ValueError("Question embedding not found: " + str(e))
    except Exception as e:
        raise Exception("Error deleting question embedding: " + str(e))
    
# Delete question embeddings by document ID
async def delete_question_embeddings_by_doc_id(doc_id: str) -> bool:
    try:
        chroma.question_embeddings_collection.delete(
            where={"doc_id": doc_id}
        )
        return True
    except Exception as e:
        raise Exception("Error deleting question embeddings for document ID " + doc_id + ": " + str(e))
    
# Reset (Delete) question embeddings collection
async def reset_question_embeddings_collection() -> bool:
    try:
        chroma.client.delete_collection("question_embeddings")
        chroma.question_embeddings_collection = chroma.client.create_collection("question_embeddings")
        return True
    except Exception as e:
        raise Exception("Error deleting all question embeddings: " + str(e))
    
# Semantic search question embeddings
async def semantic_search_question_embeddings(
    query_vector: list[float],
    top_k: int,
    relevant_embedding_ids: list[str] = None
) -> list[question_embedding_schema.QuestionEmbeddingResponse]:    
    if relevant_embedding_ids:
        # Tạo sub-collection tạm
        temp_name = f"temp_search_{uuid.uuid4().hex[:8]}"
        sub_collection = chroma.client.create_collection(name=temp_name)
        try:
            # Lấy các embedding cụ thể
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

            # Query trong sub-collection
            results = sub_collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                include=["embeddings", "metadatas"]
            )
        finally:
            chroma.client.delete_collection(temp_name)
    else:
        # Query trực tiếp trên collection chính
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