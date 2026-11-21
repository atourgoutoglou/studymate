"""StudyMate: ask questions about your PDFs and get answers with citations."""
from pathlib import Path

from app.embeddings import SemanticIndex
from app.hybrid import hybrid_search
from app.ingest import Chunk, chunk_folder
from app.llm import ask_llm

DATA_FOLDER = Path("data")


def build_context(chunks: list[Chunk]) -> str:
    """Turn the retrieved chunks into one text, each part labelled with its source."""
    return "\n\n".join(f"[{chunk.source}, page {chunk.page}] {chunk.text}" for chunk in chunks)


def main() -> None:
    print(f"Loading PDFs from '{DATA_FOLDER}':")
    chunks = chunk_folder(DATA_FOLDER)
    if not chunks:
        print("No PDFs found. Put some PDF files in the data folder.")
        return

    index = SemanticIndex(chunks)
    print(f"Ready! {len(chunks)} chunks. Type 'exit' to quit.")

    while True:
        question = input("\nYour question: ").strip()
        if question.lower() in ("exit", "quit"):
            break
        if not question:
            continue

        relevant = hybrid_search(question, chunks, index, top_k=5)
        print("Sources:", [f"{chunk.source} p.{chunk.page}" for chunk in relevant])

        answer = ask_llm(question, context=build_context(relevant))
        print(f"\n{answer}")


if __name__ == "__main__":
    main()