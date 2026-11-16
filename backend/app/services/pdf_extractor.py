
import fitz


def extract_pdf_text(file_bytes: bytes):

    try:
        document = fitz.open(
            stream=file_bytes,
            filetype="pdf"
        )

        extracted_pages = []

        for page_number, page in enumerate(document, start=1):

            text = page.get_text("text")

            extracted_pages.append({
                "page": page_number,
                "text": text.strip()
            })

        document.close()

        full_text = "\n\n".join(
            page["text"] for page in extracted_pages
        )

        return {
            "page_count": len(extracted_pages),
            "full_text": full_text,
            "pages": extracted_pages
        }

    except Exception as error:
        raise ValueError(
            f"Unable to extract PDF: {str(error)}"
        )
