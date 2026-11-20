"""Load PDF documents and extract their text."""
from pathlib import Path

from pypdf import PdfReader


def load_pdf_pages(path: Path) -> list[tuple[int, str]]:
    """Return a list of (page_number, text) for every page that has text."""
    reader = PdfReader(path)
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = " ".join(text.split())
        if text:
            pages.append((page_number, text))
    return pages


if __name__ == "__main__":
    pdf_path = Path("data/rag_paper.pdf")
    pages = load_pdf_pages(pdf_path)
    print(f"Loaded {len(pages)} pages from {pdf_path.name}")

    first_page_number, first_page_text = pages[0]
    print(f"\n--- Page {first_page_number} (first 500 characters) ---")
    print(first_page_text[:500])