
from sqlalchemy.orm import Session

from rag.embeddings import generate_query_embedding
from rag.vector_store import search_chunks
from rag.bm25_search import search_bm25


# ==========================================
# RECIPROCAL RANK FUSION
# ==========================================

def reciprocal_rank_fusion(
    vector_results,
    keyword_results,
    limit=5,
    rrf_k=60
):

    combined = {}

    # Process vector search results
    for rank, result in enumerate(vector_results, start=1):

        key = (
            str(result.get("document_id")),
            str(result.get("chunk_index"))
        )

        if key not in combined:

            combined[key] = {
                **result,
                "rrf_score": 0.0,
                "vector_score": result.get("score")
            }

        combined[key]["rrf_score"] += (
            1.0 / (rrf_k + rank)
        )

    # Process BM25 results
    for rank, result in enumerate(keyword_results, start=1):

        key = (
            str(result.get("document_id")),
            str(result.get("chunk_index"))
        )

        if key not in combined:

            combined[key] = {
                **result,
                "rrf_score": 0.0,
                "vector_score": None
            }

        combined[key]["rrf_score"] += (
            1.0 / (rrf_k + rank)
        )

        combined[key]["bm25_score"] = result.get(
            "bm25_score"
        )

    # Sort by combined relevance
    final_results = sorted(
        combined.values(),
        key=lambda item: item["rrf_score"],
        reverse=True
    )

    return final_results[:limit]


# ==========================================
# HYBRID SEARCH
# ==========================================

def hybrid_search(
    db: Session,
    query: str,
    document_id: str | None = None,
    limit: int = 5,
    candidate_limit: int = 20
):

    # ----------------------------------
    # 1. GENERATE QUERY EMBEDDING
    # ----------------------------------

    query_embedding = generate_query_embedding(query)

    # ----------------------------------
    # 2. QDRANT SEMANTIC SEARCH
    # ----------------------------------

    vector_results = search_chunks(
        query_embedding=query_embedding,
        limit=candidate_limit,
        document_id=document_id
    )

    # ----------------------------------
    # 3. BM25 KEYWORD SEARCH
    # ----------------------------------

    keyword_results = search_bm25(
        db=db,
        query=query,
        document_id=document_id,
        limit=candidate_limit
    )

    # ----------------------------------
    # 4. COMBINE USING RRF
    # ----------------------------------

    results = reciprocal_rank_fusion(
        vector_results=vector_results,
        keyword_results=keyword_results,
        limit=limit
    )

    return results
