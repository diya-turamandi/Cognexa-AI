
# Cognexa AI – Architecture

## 1. Project Overview

Cognexa AI is an AI-powered personal
knowledge management platform.

## 2. Frontend

- React.js
- Tailwind CSS
- Dashboard
- Document Library
- Upload Interface
- AI Chat Interface

## 3. Backend

- Python
- FastAPI
- REST APIs
- Document Management
- Database Integration

## 4. Database

- PostgreSQL – Structured Data
- Qdrant – Vector Embeddings

## 5. Document Workflow

1. User uploads a document.
2. React sends the document to FastAPI.
3. FastAPI receives and stores the file.
4. PostgreSQL stores document metadata.
5. Document processing extracts text.
6. Text is divided into chunks.
7. Embeddings are generated.
8. Embeddings are stored in Qdrant.
9. User asks questions.
10. RAG retrieves relevant information.
11. AI generates an answer with references.

## 6. Future Features

- Hybrid Search
- Cross-Encoder Reranking
- Document Citations
- RAG Evaluation using RAGAS
