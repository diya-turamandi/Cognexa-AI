
import uuid

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


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)

UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 15 * 1024 * 1024


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

    file_path = UPLOAD_DIR / f"{document_id}.pdf"

    try:
        extracted = extract_pdf_text(file_bytes)

        chunks = create_chunks(extracted["pages"])

        if not extracted["full_text"].strip():
            raise HTTPException(
                status_code=422,
                detail="No extractable text found. Scanned PDFs require OCR."
            )

        file_path.write_bytes(file_bytes)

        document = Document(
            id=document_id,
            filename=Path(file.filename).name,
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

        return {
            "success": True,
            "message": "Document uploaded and indexed successfully",

            "document": {
                "id": document_id,
                "filename": document.filename,
                "page_count": document.page_count,
                "file_size": document.file_size,
                "chunk_count": len(chunks),
                "status": document.status
            },

            # Retained temporarily for compatibility
            # with the existing frontend.
            "extracted_text": extracted["full_text"],
            "pages": extracted["pages"]
        }

    except HTTPException:
        db.rollback()
        file_path.unlink(missing_ok=True)
        raise

    except Exception:
        db.rollback()
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Document processing failed"
        )

    finally:
        await file.close()


@router.get("/")
def get_documents(db: Session = Depends(get_db)):

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
                "uploaded_at": doc.uploaded_at.isoformat()
                if doc.uploaded_at else None
            }
            for doc in documents
        ]
    }


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
        db.delete(document)
        db.commit()

        file_path.unlink(missing_ok=True)

        return {
            "success": True,
            "message": "Document deleted successfully"
        }

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to delete document"
        )
