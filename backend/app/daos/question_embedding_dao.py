import uuid
from app.databases import chroma
from fastapi.encoders import jsonable_encoder
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
async def get_question_embedding_by_id(embedding_id: str) -> question_embedding_schema.QuestionEmbeddingResponse | None:
    results = chroma.question_embeddings_collection.get(ids=[embedding_id], include=["embeddings", "metadatas"])
    if not results or 'ids' not in results or len(results['ids']) == 0:
        return None
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
    
# Update feedback for a question embedding
async def update_question_embedding_feedback(embedding_id: str, score: int) -> question_embedding_schema.QuestionEmbeddingResponse | None:
    existing_embedding = await get_question_embedding_by_id(embedding_id)
    if not existing_embedding:
        return None
    existing_embedding.metadata.feedback_score += score
    existing_embedding.metadata.feedback_count += 1
    chroma.question_embeddings_collection.update(
        ids=[embedding_id],
        metadatas=[existing_embedding.metadata.model_dump()]
    )
    return existing_embedding
# Delete a question embedding by ID
async def delete_question_embedding(embedding_id: str) -> bool:
    try:
        chroma.question_embeddings_collection.delete(ids=[embedding_id])
        return True
    except Exception as e:
        raise RuntimeError(f"Error deleting question embedding with ID {embedding_id}: {e}")
    
# Reset (Delete) question embeddings collection
async def reset_question_embeddings_collection() -> bool:
    try:
        chroma.client.delete_collection("question_embeddings")
        chroma.question_embeddings_collection = chroma.client.create_collection("question_embeddings")
        return True
    except Exception as e:
        raise RuntimeError(f"Error deleting all question embeddings: {e}")