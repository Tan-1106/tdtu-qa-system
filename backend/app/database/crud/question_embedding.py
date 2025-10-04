import uuid

from app.database.chroma import question_embeddings_collection
from app.schemas.question_embedding import QuestionEmbeddingCreate, QuestionEmbeddingFeedbackUpdate, QuestionEmbeddingResponse

# Read all question embeddings
async def get_question_embeddings() -> list[QuestionEmbeddingResponse]:
    results = question_embeddings_collection.get(include=["embeddings", "metadatas"])
    print(results)
    
    if not results or 'ids' not in results:
        return []
    
    embeddings = []
    for idx in range(len(results['ids'])):
        embeddings.append(
            QuestionEmbeddingResponse(
                id=results['ids'][idx],
                vector=results['embeddings'][idx],
                metadata=results['metadatas'][idx]
            )
        )
        
    return embeddings

# Read a question embedding by ID

# Create a new question embedding
async def create_question_embedding(embedding: QuestionEmbeddingCreate) -> QuestionEmbeddingResponse:
    embedding_id = str(uuid.uuid4())
    
    question_embeddings_collection.add(
        ids=[embedding_id],
        embeddings=[embedding.vector],
        metadatas=[embedding.metadata.model_dump()],
    )
    
    return QuestionEmbeddingResponse(
        id=embedding_id,
        vector=embedding.vector,
        metadata=embedding.metadata
    )
    

# Update an existing question embedding

# Delete a question embedding by ID