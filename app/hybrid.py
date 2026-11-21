"""Hybrid search: combine keyword and semantic results with Reciprocal Rank Fusion."""
from app.embeddings import SemanticIndex
from app.ingest import Chunk
from app.search import keyword_search

RRF_K = 60          # standard constant from the RRF paper
CANDIDATES = 20     # how many results we take from each method before fusing


def hybrid_search(question: str, chunks: list[Chunk], index: SemanticIndex, top_k: int = 5) -> list[Chunk]:
    """Rank chunks by how high they appear in BOTH keyword and semantic results."""
    keyword_results = keyword_search(question, chunks, top_k=CANDIDATES)
    semantic_results = index.search(question, top_k=CANDIDATES)

    scores: dict[int, float] = {}
    for results in (keyword_results, semantic_results):
        for rank, chunk in enumerate(results, start=1):
            position = chunks.index(chunk)
            scores[position] = scores.get(position, 0) + 1 / (RRF_K + rank)

    best = sorted(scores, key=scores.get, reverse=True)[:top_k]
    return [chunks[position] for position in best]