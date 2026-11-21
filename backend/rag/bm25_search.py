
import re

from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session

from app.models import Document, DocumentChunk


# ==========================================
# TEXT TOKENIZATION
# ==========================================

def tokenize(text: str):

    return re.findall(
        r"\b[a-zA-Z0-9_]+\b",
        text.lower()
    )


# ==========================================
# BM25 KEYWORD SEARCH
# ==========================================

def search_bm25(
    db: Session,
    query: str,
    document_id: str | None = None,
    limit: int = 20
):

    # Get document chunks from PostgreSQL
    db_query = (
        db.query(DocumentChunk, Document.filename)
        .join(
            Document,
            Document.id == DocumentChunk.document_id
        )
    )

    # Optional document filtering
    if document_id:
        db_query = db_query.filter(
            DocumentChunk.document_id == str(document_id)
        )

    rows = db_query.all()

    if not rows:
        return []

    # Prepare corpus
    chunks = []

    corpus = []

    for chunk, filename in rows:

        text = chunk.content or ""

        tokens = tokenize(text)

        if not tokens:
            continue

        chunks.append({
            "document_id": str(chunk.document_id),
            "filename": filename,
            "page": chunk.page_number,
            "chunk_index": chunk.chunk_index,
            "text": text,
            "start_index": chunk.start_index,
            "end_index": chunk.end_index
        })

        corpus.append(tokens)

    if not corpus:
        return []

    # Create BM25 index
    bm25 = BM25Okapi(corpus)

    # Tokenize user query
    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    # Calculate keyword relevance scores
    scores = bm25.get_scores(query_tokens)

    # Rank results
    ranked_results = sorted(
        enumerate(scores),
        key=lambda item: item[1],
        reverse=True
    )

    results = []

    for index, score in ranked_results:

        # Ignore chunks with no keyword relevance
        if score <= 0:
            continue

        result = chunks[index].copy()

        result["bm25_score"] = float(score)

        results.append(result)

        if len(results) >= limit:
            break

    return results
