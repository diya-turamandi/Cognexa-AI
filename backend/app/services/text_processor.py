
import re


def clean_text(text: str) -> str:
    """Clean extracted PDF text."""

    text = text.replace("\x00", "")

    # Remove unnecessary spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Reduce excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def create_chunks(pages, chunk_size=1000, overlap=150):
    """
    Split PDF pages into smaller text chunks.

    Each chunk stores:
    - chunk_index
    - content
    - page_number
    - start_index
    - end_index
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    chunks = []

    for page in pages:

        text = clean_text(page["text"])

        if not text:
            continue

        start = 0

        while start < len(text):

            end = min(start + chunk_size, len(text))

            # Try to split at a natural text boundary
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
