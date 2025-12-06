from app.services import embedding_service


# Retrieve embedding vectors with pagination
async def get_embedding_vectors(page: int, limit: int):
    vectors = await embedding_service.get_embedding_vectors(page, limit)
    return vectors


# Reset embeddings collection
async def reset_embeddings():
    success = await embedding_service.reset_embeddings()
    return success


# Recreate embeddings for document chunks
async def recreate_embeddings():
    success = await embedding_service.recreate_embeddings()
    return success