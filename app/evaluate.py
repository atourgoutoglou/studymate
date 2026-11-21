"""Measure how often each search method finds the right page."""
import json
import random
from pathlib import Path

from app.embeddings import SemanticIndex
from app.ingest import Chunk, chunk_pdf
from app.llm import chat
from app.search import keyword_search

PDF_PATH = Path("data/rag_paper.pdf")
QUESTIONS_FILE = Path("eval/questions.json")
NUM_QUESTIONS = 20
TOP_K = 5

QUESTION_PROMPT = (
    "You write exam questions. Given a passage from a research paper, write ONE "
    "specific question that can be answered using only this passage. "
    "Do not mention 'the passage' or 'the text'. Reply with the question only."
)


def generate_questions(chunks: list[Chunk], n: int) -> list[dict]:
    """Ask the LLM to write one question for each of `n` random chunks."""
    random.seed(42)  # same random chunks every time -> reproducible results
    items = []
    for chunk in random.sample(chunks, n):
        question = chat(QUESTION_PROMPT, chunk.text).strip()
        items.append({"question": question, "page": chunk.page})
        print(f"[Page {chunk.page}] {question}")
    return items


def load_or_create_questions(chunks: list[Chunk]) -> list[dict]:
    """Load the test questions from disk, or generate and save them the first time."""
    if QUESTIONS_FILE.exists():
        return json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))

    print(f"Generating {NUM_QUESTIONS} test questions (only the first time)...\n")
    items = generate_questions(chunks, NUM_QUESTIONS)
    QUESTIONS_FILE.parent.mkdir(exist_ok=True)
    QUESTIONS_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    return items


def evaluate(name: str, search, items: list[dict], k: int = TOP_K) -> None:
    """Print Hit@k and MRR for one search method."""
    hits = 0
    reciprocal_ranks = []
    for item in items:
        pages = [chunk.page for chunk in search(item["question"], k)]
        if item["page"] in pages:
            hits += 1
            rank = pages.index(item["page"]) + 1
            reciprocal_ranks.append(1 / rank)
        else:
            reciprocal_ranks.append(0)

    hit_rate = hits / len(items)
    mrr = sum(reciprocal_ranks) / len(items)
    print(f"{name:<10} Hit@{k}: {hit_rate:.0%}   MRR: {mrr:.2f}")


def main() -> None:
    chunks = chunk_pdf(PDF_PATH)
    items = load_or_create_questions(chunks)
    index = SemanticIndex(chunks)

    print(f"\nResults on {len(items)} questions:\n")
    evaluate("Keyword", lambda question, k: keyword_search(question, chunks, top_k=k), items)
    evaluate("Semantic", lambda question, k: index.search(question, top_k=k), items)


if __name__ == "__main__":
    main()