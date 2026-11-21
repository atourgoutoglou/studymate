"""StudyMate: ask questions about your PDF and get answers with page citations."""
from pathlib import Path

from app.embeddings import SemanticIndex
from app.ingest import Chunk, chunk_pdf
from app.llm import ask_llm
from app.search import keyword_search
from app.hybrid import hybrid_search


def build_context(chunks: list[Chunk]) -> str:
    """Turn the retrieved chunks into one text, each part labelled with its page."""
    return "\n\n".join(f"[Page {chunk.page}] {chunk.text}" for chunk in chunks)


def main() -> None:
    pdf_path = Path("data/rag_paper.pdf")
    chunks = chunk_pdf(pdf_path)
    print(f"Loaded {pdf_path.name}: {len(chunks)} chunks.")

    print("Building semantic index...")
    index = SemanticIndex(chunks)
    print("Ready! Type 'exit' to quit.")

    while True:
        question = input("\nYour question: ").strip()
        if question.lower() in ("exit", "quit"):
            break
        if not question:
            continue

        keyword_pages = [chunk.page for chunk in keyword_search(question, chunks)]
        relevant = hybrid_search(question, chunks, index, top_k=5)
        print(f"Keyword search pages:  {keyword_pages}")
        print(f"Hybrid search pages:   {[chunk.page for chunk in relevant]}")

        answer = ask_llm(question, context=build_context(relevant))
        print(f"\n{answer}")


if __name__ == "__main__":
    main()