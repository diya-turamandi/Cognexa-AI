
import fitz


def extract_text_from_pdf(file_path: str):
    """Extract text from every page of a PDF."""
    document = fitz.open(file_path)
    pages = []

    try:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "page": page_number,
                    "text": text
                })
    finally:
        document.close()

    return pages


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150):
    """Split text into overlapping chunks."""
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunk_size or overlap")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks


def process_pdf(file_path: str):
    pages = extract_text_from_pdf(file_path)
    all_chunks = []

    for page in pages:
        page_chunks = chunk_text(page["text"])

        for index, chunk in enumerate(page_chunks):
            all_chunks.append({
                "text": chunk,
                "page": page["page"],
                "chunk_index": index
            })

    return all_chunks
