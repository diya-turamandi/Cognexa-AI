
from pathlib import Path
from uuid import uuid4

from qdrant_client import QdrantClient, models


# ==========================================
# CONFIGURATION
# ==========================================

COLLECTION_NAME = "mindvault_documents"
VECTOR_SIZE = 384

BASE_DIR = Path(__file__).resolve().parent.parent
QDRANT_PATH = BASE_DIR / "qdrant_data"


# ==========================================
# QDRANT CLIENT
# ==========================================

client = QdrantClient(path=str(QDRANT_PATH))


# ==========================================
# CREATE COLLECTION
# ==========================================

def create_collection():

    collections = client.get_collections().collections

    exists = any(
        collection.name == COLLECTION_NAME
        for collection in collections
    )

    if not exists:

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE
            )
        )

        print("Qdrant collection created successfully!")

    return COLLECTION_NAME


# ==========================================
# STORE DOCUMENT CHUNKS
# ==========================================

def store_chunks(chunks, embeddings, document_id, filename):

    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings count mismatch")

    if not chunks:
        return 0

    create_collection()

    points = []

    for chunk, embedding in zip(chunks, embeddings):

        # Support the text_processor.py field names
        # while retaining compatibility with older chunks.

        content = chunk.get("content", chunk.get("text"))

        page_number = chunk.get(
            "page_number",
            chunk.get("page")
        )

        if not content:
            raise ValueError("Chunk content is missing")

        points.append(
            models.PointStruct(
                id=str(uuid4()),

                vector=embedding,

                payload={
                    "document_id": str(document_id),
                    "filename": filename,
                    "page": page_number,
                    "chunk_index": chunk["chunk_index"],
                    "text": content,
                    "start_index": chunk.get("start_index"),
                    "end_index": chunk.get("end_index")
                }
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True
    )

    print(f"Stored {len(points)} vectors in Qdrant.")

    return len(points)


# ==========================================
# SEARCH DOCUMENT CHUNKS
# ==========================================

def search_chunks(
    query_embedding,
    limit=5,
    document_id=None
):

    create_collection()

    query_filter = None

    if document_id:

        query_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(
                        value=str(document_id)
                    )
                )
            ]
        )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=query_filter,
        limit=limit,
        with_payload=True
    )

    return [
        {
            "score": point.score,
            **(point.payload or {})
        }
        for point in results.points
    ]


# ==========================================
# DELETE DOCUMENT VECTORS
# ==========================================

def delete_document_vectors(document_id):

    create_collection()

    client.delete(
        collection_name=COLLECTION_NAME,

        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(
                            value=str(document_id)
                        )
                    )
                ]
            )
        ),

        wait=True
    )

    print(f"Deleted vectors for document: {document_id}")


# ==========================================
# CLOSE VECTOR STORE
# ==========================================

def close_vector_store():

    client.close()
