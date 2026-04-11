# extractor_text.py
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from a PDF using PyMuPDF.
    Handles multi-page PDFs and preserves layout where possible.
    """
    try:
        doc = fitz.open(pdf_path)
        full_text = []

        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            if text.strip():
                full_text.append(f"--- Page {page_num + 1} ---\n{text}")

        doc.close()
        return "\n".join(full_text)

    except Exception as e:
        raise RuntimeError(f"Error extracting text: {e}")
