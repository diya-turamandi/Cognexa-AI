
import re


def clean_text(text: str) -> str:
    """Clean extracted PDF text."""

    text = text.replace("\x00", "")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def create_chunks(
    pages,
    chunk_size=1000,
    overlap=150
):
    """
    Create overlapping chunks while preserving
    original page numbers and character positions.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []

    for page in pages:

        text = clean_text(page["text"])

        if not text:
            continue

        start = 0

        while start < len(text):

            end = min(start + chunk_size, len(text))

            # Prefer ending at a paragraph or word boundary.
            if end < len(text):
                boundary = max(
                    text.rfind("\n", start, end),
                    text.rfind(" ", start, end)
                )

                if boundary > start + chunk_size // 2:
                    end = boundary

            content = text[start:end].strip()

            if content:
                chunks.append({
                    "chunk_index": len(chunks),
                    "content": content,
                    "page_number": page["page"],
                    "start_index": start,
                    "end_index": end
                })

            if end >= len(text):
                break

            start = end - overlap

    return chunks
