
from pathlib import Path
from uuid import uuid4

from qdrant_client import QdrantClient, models

COLLECTION_NAME = "mindvault_documents"
VECTOR_SIZE = 384

BASE_DIR = Path(__file__).resolve().parent.parent
QDRANT_PATH = BASE_DIR / "qdrant_data"

client = QdrantClient(path=str(QDRANT_PATH))


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
    else:
        print("Qdrant collection already exists!")


def store_chunks(chunks, embeddings, document_id, filename):
    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings count mismatch")

    if not chunks:
        return 0

    create_collection()

    points = []

    for chunk, embedding in zip(chunks, embeddings):
        points.append(
            models.PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "document_id": str(document_id),
                    "filename": filename,
                    "page": chunk["page"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"]
                }
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    return len(points)


def search_chunks(query_embedding, limit=5, document_id=None):
    create_collection()

    query_filter = None

    if document_id:
        query_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=str(document_id))
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
            **point.payload
        }
        for point in results.points
    ]


def close_vector_store():
    client.close()
