
from rag.embeddings import generate_query_embedding
from rag.vector_store import search_chunks


def retrieve_relevant_chunks(
    query: str,
    limit: int = 5,
    document_id: str = None
):
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")

    query_embedding = generate_query_embedding(query)

    results = search_chunks(
        query_embedding=query_embedding,
        limit=limit,
        document_id=document_id
    )

    return results
