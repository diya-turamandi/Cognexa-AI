
from rag.embeddings import generate_embeddings
from rag.embeddings import generate_query_embedding

texts = [
    "Artificial intelligence helps automate tasks.",
    "Machine learning is a subset of artificial intelligence."
]

# Generate document embeddings
embeddings = generate_embeddings(texts)

print("Number of embeddings:", len(embeddings))
print("Vector dimensions:", len(embeddings[0]))

# Generate query embedding
query = "What is artificial intelligence?"

query_embedding = generate_query_embedding(query)

print("Query vector dimensions:", len(query_embedding))

print("Embedding test successful!")
