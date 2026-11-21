
from app.core.database import SessionLocal

from rag.embeddings import generate_query_embedding
from rag.vector_store import search_chunks
from rag.bm25_search import search_bm25
from rag.hybrid_search import hybrid_search


db = SessionLocal()

try:

    question = "Explain the main concepts in the document."

    # Test BM25
    print("\n========== BM25 SEARCH ==========")

    bm25_results = search_bm25(
        db=db,
        query=question,
        limit=5
    )

    for result in bm25_results:

        print({
            "filename": result["filename"],
            "page": result["page"],
            "score": result["bm25_score"]
        })

    # Test Qdrant
    print("\n========== VECTOR SEARCH ==========")

    embedding = generate_query_embedding(question)

    vector_results = search_chunks(
        query_embedding=embedding,
        limit=5
    )

    for result in vector_results:

        print({
            "filename": result.get("filename"),
            "page": result.get("page"),
            "score": result.get("score")
        })

    # Test Hybrid
    print("\n========== HYBRID SEARCH ==========")

    hybrid_results = hybrid_search(
        db=db,
        query=question,
        limit=5
    )

    for result in hybrid_results:

        print({
            "filename": result.get("filename"),
            "page": result.get("page"),
            "rrf_score": result.get("rrf_score")
        })

finally:

    db.close()
