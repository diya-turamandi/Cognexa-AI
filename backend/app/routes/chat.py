
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from rag.embeddings import generate_query_embedding
from rag.vector_store import search_chunks

from app.services.llm_service import generate_answer


router = APIRouter(
    prefix="/api/chat",
    tags=["AI Chat"]
)


class ChatRequest(BaseModel):

    question: str = Field(
        min_length=2,
        max_length=2000
    )

    document_id: str | None = None

    top_k: int = Field(
        default=5,
        ge=1,
        le=10
    )


@router.post("/")
async def chat_with_documents(request: ChatRequest):

    try:

        # STEP 1: Generate question embedding

        query_embedding = generate_query_embedding(
            request.question
        )

        # STEP 2: Retrieve relevant chunks

        results = search_chunks(
            query_embedding=query_embedding,
            limit=request.top_k,
            document_id=request.document_id
        )

        if not results:

            return {
                "success": True,
                "answer": (
                    "I could not find relevant information "
                    "in the uploaded documents."
                ),
                "sources": []
            }

        # STEP 3: Prepare document context

        context_parts = []

        sources = []

        for result in results:

            context_parts.append(
                f"""
Filename: {result.get('filename')}
Page: {result.get('page')}

Content:
{result.get('text')}
"""
            )

            sources.append({
                "filename": result.get("filename"),
                "page": result.get("page"),
                "chunk_index": result.get("chunk_index"),
                "score": result.get("score"),
                "content": result.get("text")
            })

        context = "\n\n".join(context_parts)

        # STEP 4: Generate answer using Ollama

        answer = await generate_answer(
            question=request.question,
            context=context
        )

        # STEP 5: Return response

        return {
            "success": True,
            "question": request.question,
            "answer": answer,
            "sources": sources
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )
