
from sentence_transformers import CrossEncoder

# Load model once
reranker_model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank_chunks(
    query: str,
    documents: list,
    top_k: int = 5
):
    if not documents:
        return []

    pairs = [
        (query, doc.get("text", ""))
        for doc in documents
    ]

    scores = reranker_model.predict(pairs)

    reranked = []

    for document, score in zip(documents, scores):
        item = document.copy()
        item["rerank_score"] = float(score)
        reranked.append(item)

    reranked.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return reranked[:top_k]
