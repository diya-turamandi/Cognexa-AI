
import uuid
import logging

from pathlib import Path

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Document, DocumentChunk

from app.services.pdf_extractor import extract_pdf_text
from app.services.text_processor import create_chunks

# RAG imports
from rag.embeddings import generate_embeddings
from rag.vector_store import (
    store_chunks,
    delete_document_vectors
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)


# ==========================================
# CONFIGURATION
# ==========================================

UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 15 * 1024 * 1024


# ==========================================
# 1. UPLOAD AND INDEX PDF
# ==========================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    file_bytes = await file.read(MAX_FILE_SIZE + 1)

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds 15 MB limit"
        )

    if not file_bytes.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file"
        )

    document_id = str(uuid.uuid4())

    original_filename = Path(file.filename).name

    file_path = UPLOAD_DIR / f"{document_id}.pdf"

    file_saved = False
    db_committed = False
    qdrant_attempted = False

    try:

        # ----------------------------------
        # STEP 1: EXTRACT PDF TEXT
        # ----------------------------------

        extracted = extract_pdf_text(file_bytes)

        if not extracted["full_text"].strip():
            raise HTTPException(
                status_code=422,
                detail=(
                    "No extractable text found. "
                    "Scanned PDFs require OCR."
                )
            )

        # ----------------------------------
        # STEP 2: CREATE TEXT CHUNKS
        # ----------------------------------

        chunks = create_chunks(extracted["pages"])

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="No valid text chunks could be generated"
            )

        # ----------------------------------
        # STEP 3: GENERATE EMBEDDINGS
        # ----------------------------------

        texts = [
            chunk["content"]
            for chunk in chunks
        ]

        embeddings = generate_embeddings(texts)

        if len(embeddings) != len(chunks):
            raise ValueError(
                "Embedding generation failed for some chunks"
            )

        # ----------------------------------
        # STEP 4: SAVE PDF FILE
        # ----------------------------------

        file_path.write_bytes(file_bytes)
        file_saved = True

        # ----------------------------------
        # STEP 5: SAVE DOCUMENT IN POSTGRESQL
        # ----------------------------------

        document = Document(
            id=document_id,
            filename=original_filename,
            file_path=str(file_path),
            file_size=len(file_bytes),
            page_count=extracted["page_count"],
            status="processed"
        )

        db.add(document)

        for chunk in chunks:

            db.add(
                DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk["chunk_index"],
                    content=chunk["content"],
                    page_number=chunk["page_number"],
                    start_index=chunk["start_index"],
                    end_index=chunk["end_index"]
                )
            )

        db.commit()
        db_committed = True

        # ----------------------------------
        # STEP 6: STORE VECTORS IN QDRANT
        # ----------------------------------

        qdrant_attempted = True

        vector_count = store_chunks(
            chunks=chunks,
            embeddings=embeddings,
            document_id=document_id,
            filename=original_filename
        )

        # ----------------------------------
        # STEP 7: SUCCESS RESPONSE
        # ----------------------------------

        return {
            "success": True,
            "message": "Document uploaded and indexed successfully",

            "document": {
                "id": document_id,
                "filename": original_filename,
                "page_count": extracted["page_count"],
                "file_size": len(file_bytes),
                "chunk_count": len(chunks),
                "vector_count": vector_count,
                "status": "processed"
            },

            # Retained for existing frontend compatibility
            "extracted_text": extracted["full_text"],
            "pages": extracted["pages"]
        }

    except HTTPException:

        db.rollback()

        # Remove committed PostgreSQL records if necessary
        if db_committed:
            try:
                saved_document = db.query(Document).filter(
                    Document.id == document_id
                ).first()

                if saved_document:
                    db.delete(saved_document)
                    db.commit()

            except Exception:
                db.rollback()
                logger.exception(
                    "Failed to clean up PostgreSQL document"
                )

        if file_saved:
            file_path.unlink(missing_ok=True)

        raise

    except Exception:

        logger.exception(
            "PDF upload or RAG indexing failed"
        )

        db.rollback()

        # Remove potentially inserted Qdrant vectors
        if qdrant_attempted:
            try:
                delete_document_vectors(document_id)

            except Exception:
                logger.exception(
                    "Failed to clean up Qdrant vectors"
                )

        # Remove PostgreSQL document and chunks
        if db_committed:
            try:
                saved_document = db.query(Document).filter(
                    Document.id == document_id
                ).first()

                if saved_document:
                    db.delete(saved_document)
                    db.commit()

            except Exception:
                db.rollback()
                logger.exception(
                    "Failed to clean up PostgreSQL records"
                )

        # Remove uploaded PDF
        if file_saved:
            file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail=(
                "Document processing or vector indexing failed. "
                "Please check the backend logs and try again."
            )
        )

    finally:
        await file.close()


# ==========================================
# 2. GET ALL DOCUMENTS
# ==========================================

@router.get("/")
def get_documents(
    db: Session = Depends(get_db)
):

    documents = (
        db.query(Document)
        .order_by(Document.uploaded_at.desc())
        .all()
    )

    return {
        "success": True,
        "total": len(documents),

        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "page_count": doc.page_count,
                "file_size": doc.file_size,
                "status": doc.status,
                "uploaded_at": (
                    doc.uploaded_at.isoformat()
                    if doc.uploaded_at else None
                )
            }
            for doc in documents
        ]
    }


# ==========================================
# 3. GET DOCUMENT CHUNKS
# ==========================================

@router.get("/{document_id}/chunks")
def get_document_chunks(
    document_id: str,
    db: Session = Depends(get_db)
):

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )

    return {
        "success": True,
        "document_id": document_id,
        "total_chunks": len(chunks),

        "chunks": [
            {
                "id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "page_number": chunk.page_number,
                "start_index": chunk.start_index,
                "end_index": chunk.end_index
            }
            for chunk in chunks
        ]
    }


# ==========================================
# 4. DELETE DOCUMENT AND ITS VECTORS
# ==========================================

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    file_path = Path(document.file_path)

    try:

        # Delete Qdrant vectors first
        delete_document_vectors(document_id)

        # Delete PostgreSQL document and related chunks
        db.delete(document)
        db.commit()

        # Delete original PDF
        file_path.unlink(missing_ok=True)

        return {
            "success": True,
            "message": (
                "Document, chunks and associated vectors "
                "deleted successfully"
            ),
            "document_id": document_id
        }

    except Exception:

        db.rollback()

        logger.exception(
            "Document deletion failed: %s",
            document_id
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to delete document completely"
        )
