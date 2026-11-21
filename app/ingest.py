"""Load PDF documents, extract their text and split it into chunks."""
from dataclasses import dataclass
from pathlib import Path
import re

from pypdf import PdfReader

CHUNK_SIZE = 200     # words per chunk
CHUNK_OVERLAP = 40   # words shared with the previous chunk

# Reference markers like [1], [24, 25], [3–5] or [citation needed]
CITATION_MARKER = re.compile(r"\[(?:\d+(?:\s*[,–-]\s*\d+)*|citation needed)\]")

@dataclass
class Chunk:
    """A small piece of a document that remembers where it came from."""

    source: str  # file name
    page: int    # page number, used later for citations
    text: str

def clean_text(text: str) -> str:
    """Remove reference markers and extra whitespace from extracted text."""
    text = CITATION_MARKER.sub("", text)
    text = " ".join(text.split())
    return re.sub(r"\s+([,.;:])", r"\1", text)


def load_pdf_pages(path: Path) -> list[tuple[int, str]]:
    """Return a list of (page_number, text) for every page that has text."""
    reader = PdfReader(path)
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = clean_text(text)
        if text:
            pages.append((page_number, text))
    return pages


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks of `chunk_size` words."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")
    words = text.split()
    step = chunk_size - overlap
    chunks = []
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start:start + chunk_size]))
        if start + chunk_size >= len(words):
            break
    return chunks


def chunk_pdf(path: Path) -> list[Chunk]:
    """Load a PDF and split every page into chunks that remember their page."""
    chunks = []
    for page_number, text in load_pdf_pages(path):
        for piece in split_text(text):
            chunks.append(Chunk(source=path.name, page=page_number, text=piece))
    return chunks

def chunk_folder(folder: Path) -> list[Chunk]:
    """Load and chunk every PDF in a folder."""
    chunks = []
    for pdf_path in sorted(Path(folder).glob("*.pdf")):
        file_chunks = chunk_pdf(pdf_path)
        print(f"  {pdf_path.name}: {len(file_chunks)} chunks")
        chunks.extend(file_chunks)
    return chunks


if __name__ == "__main__":
    pdf_path = Path("data/rag_paper.pdf")
    chunks = chunk_pdf(pdf_path)
    print(f"{pdf_path.name}: {len(chunks)} chunks")

    for chunk in chunks[:2]:
        print(f"\n--- Page {chunk.page} ({len(chunk.text.split())} words) ---")
        print(chunk.text[:300], "...")