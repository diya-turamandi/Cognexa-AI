
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models import ChatSession
from app.schemas.chat import ChatRequest, ChatResponse

from app.services.reranker import rerank_chunks

from app.services.chat_service import (
    save_message,
    get_chat_history,
    format_chat_history,
    update_session_title
)

from app.services.llm_service import generate_answer
from rag.hybrid_search import hybrid_search


router = APIRouter(
    prefix="/api/chat",
    tags=["AI Chat"]
)


# ==========================================
# CHAT WITH DOCUMENTS + HISTORY
# ==========================================

@router.post("/", response_model=ChatResponse)
async def chat_with_documents(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    try:

        # 1. FIND CHAT SESSION

        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == request.session_id)
            .first()
        )

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Chat session not found"
            )

        # 2. GET PREVIOUS CONVERSATION

        previous_messages = get_chat_history(
            db=db,
            session_id=session.id,
            limit=10
        )

        history = format_chat_history(previous_messages)

        # 3. UPDATE SESSION TITLE

        update_session_title(
            db=db,
            session=session,
            question=request.question
        )

        # 4. HYBRID SEARCH - RETRIEVE 20 CANDIDATES

        candidates = hybrid_search(
            db=db,
            query=request.question,
            document_id=session.document_id,
            limit=20,
            candidate_limit=20
        )

        print(f"Hybrid search retrieved {len(candidates)} candidates")

        # 5. CROSS-ENCODER RERANKING - TOP 5

        results = rerank_chunks(
            query=request.question,
            documents=candidates,
            top_k=5
        )

        print(f"Cross-Encoder selected {len(results)} chunks")

        # 6. PREPARE DOCUMENT CONTEXT

        context_parts = []
        sources = []

        for result in results:

            filename = result.get("filename")
            page = result.get("page")
            content = result.get("text", "")

            context_parts.append(
                f"""
Filename: {filename}
Page: {page}

Content:
{content}
"""
            )

            sources.append({
                "filename": filename,
                "page": page,
                "chunk_index": result.get("chunk_index"),
                "score": result.get("rerank_score"),
                "content": content
            })

        if context_parts:
            context = "\n\n".join(context_parts)
        else:
            context = (
                "No relevant information was found "
                "in the uploaded documents."
            )

        # 7. GENERATE AI ANSWER USING OLLAMA

        answer = await generate_answer(
            question=request.question,
            context=context,
            history=history
        )

        # 8. SAVE USER MESSAGE

        save_message(
            db=db,
            session_id=session.id,
            role="user",
            content=request.question
        )

        # 9. SAVE AI RESPONSE

        save_message(
            db=db,
            session_id=session.id,
            role="assistant",
            content=answer
        )

        # 10. UPDATE SESSION TIMESTAMP

        session.updated_at = func.now()

        # 11. COMMIT CONVERSATION

        db.commit()

        return {
            "success": True,
            "session_id": session.id,
            "question": request.question,
            "answer": answer,
            "sources": sources
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )
