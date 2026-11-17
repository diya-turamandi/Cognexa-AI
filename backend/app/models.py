
from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    func
)

from sqlalchemy.orm import relationship

from app.core.database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)

    filename = Column(String(255), nullable=False)

    file_path = Column(String(500), nullable=False)

    file_size = Column(Integer, nullable=False)

    page_count = Column(Integer, default=0)

    status = Column(
        String(50),
        default="processed"
    )

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan"
    )


class DocumentChunk(Base):

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        String,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    chunk_index = Column(Integer, nullable=False)

    content = Column(Text, nullable=False)

    page_number = Column(Integer, nullable=False)

    start_index = Column(Integer, nullable=False)

    end_index = Column(Integer, nullable=False)

    document = relationship(
        "Document",
        back_populates="chunks"
    )
