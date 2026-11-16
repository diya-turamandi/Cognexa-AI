
import os
import uuid

from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.pdf_extractor import extract_pdf_text


router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 15 * 1024 * 1024


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    file_bytes = await file.read(MAX_FILE_SIZE + 1)

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size cannot exceed 15 MB"
        )

    if not file_bytes.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file"
        )

    try:
        extracted_data = extract_pdf_text(file_bytes)

        document_id = str(uuid.uuid4())

        safe_filename = f"{document_id}.pdf"

        file_path = UPLOAD_DIR / safe_filename

        with open(file_path, "wb") as pdf_file:
            pdf_file.write(file_bytes)

        return {
            "success": True,
            "message": "PDF uploaded and processed successfully",

            "document": {
                "id": document_id,
                "filename": file.filename,
                "page_count": extracted_data["page_count"],
                "file_size": len(file_bytes),
                "extracted_characters": len(
                    extracted_data["full_text"]
                )
            },

            "extracted_text": extracted_data["full_text"],

            "pages": extracted_data["pages"]
        }

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Document processing failed"
        )

    finally:
        await file.close()
