
from sqlalchemy.orm import Session

from app.models import ChatSession, ChatMessage


# ==========================================
# SAVE MESSAGE
# ==========================================

def save_message(
    db: Session,
    session_id: str,
    role: str,
    content: str
):

    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content
    )

    db.add(message)

    return message


# ==========================================
# GET RECENT CHAT HISTORY
# ==========================================

def get_chat_history(
    db: Session,
    session_id: str,
    limit: int = 10
):

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
        .limit(limit)
        .all()
    )

    messages.reverse()

    return messages


# ==========================================
# FORMAT HISTORY FOR LLM
# ==========================================

def format_chat_history(messages):

    if not messages:
        return "No previous conversation."

    history = []

    for message in messages:

        role = (
            "User"
            if message.role == "user"
            else "Assistant"
        )

        history.append(
            f"{role}: {message.content}"
        )

    return "\n".join(history)


# ==========================================
# UPDATE SESSION TITLE
# ==========================================

def update_session_title(
    db: Session,
    session: ChatSession,
    question: str
):

    if session.title == "New Chat":

        session.title = question[:70]

    return session
