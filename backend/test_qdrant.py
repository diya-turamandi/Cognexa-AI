
from rag.embeddings import generate_embeddings
from rag.vector_store import store_chunks
from rag.vector_store import search_chunks

# Sample chunks matching your text processor
chunks = [
    {
        "chunk_index": 0,
        "content": "Artificial intelligence is a field of computer science.",
        "page_number": 1,
        "start_index": 0,
        "end_index": 60
    },
    {
        "chunk_index": 1,
        "content": "Machine learning allows computers to learn from data.",
        "page_number": 2,
        "start_index": 0,
        "end_index": 55
    }
]

document_id = "test-document-001"
filename = "test.pdf"

# Generate embeddings
texts = [chunk["content"] for chunk in chunks]
embeddings = generate_embeddings(texts)

# Store vectors
count = store_chunks(
    chunks,
    embeddings,
    document_id,
    filename
)

print("Vectors stored:", count)

# Search vectors
from rag.embeddings import generate_query_embedding

query = "What is machine learning?"

query_embedding = generate_query_embedding(query)

results = search_chunks(
    query_embedding,
    limit=2,
    document_id=document_id
)

print("\nSearch results:")

for result in results:
    print("Score:", result["score"])
    print("Page:", result["page"])
    print("Text:", result["text"])
    print("------------------")
