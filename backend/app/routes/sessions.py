
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import ChatSession, Document
from app.schemas.chat import (
    SessionCreate,
    SessionResponse,
    SessionDetailResponse
)


router = APIRouter(
    prefix="/api/sessions",
    tags=["Chat Sessions"]
)


# ==========================================
# 1. CREATE CHAT SESSION
# ==========================================

@router.post("/", response_model=SessionResponse)
def create_session(
    request: SessionCreate,
    db: Session = Depends(get_db)
):

    if request.document_id:

        document = (
            db.query(Document)
            .filter(Document.id == request.document_id)
            .first()
        )

        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

    session = ChatSession(
        id=str(uuid4()),
        title=request.title,
        document_id=request.document_id
    )

    try:

        db.add(session)
        db.commit()
        db.refresh(session)

        return session

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Could not create chat session"
        )


# ==========================================
# 2. GET ALL CHAT SESSIONS
# ==========================================

@router.get("/", response_model=list[SessionResponse])
def get_sessions(
    db: Session = Depends(get_db)
):

    sessions = (
        db.query(ChatSession)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )

    return sessions


# ==========================================
# 3. GET SESSION WITH MESSAGES
# ==========================================

@router.get(
    "/{session_id}",
    response_model=SessionDetailResponse
)
def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):

    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id)
        .first()
    )

    if not session:

        raise HTTPException(
            status_code=404,
            detail="Chat session not found"
        )

    return session


# ==========================================
# 4. DELETE CHAT SESSION
# ==========================================

@router.delete("/{session_id}")
def delete_session(
    session_id: str,
    db: Session = Depends(get_db)
):

    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id)
        .first()
    )

    if not session:

        raise HTTPException(
            status_code=404,
            detail="Chat session not found"
        )

    try:

        db.delete(session)
        db.commit()

        return {
            "success": True,
            "message": "Chat session deleted successfully",
            "session_id": session_id
        }

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Could not delete chat session"
        )
