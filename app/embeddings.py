"""Semantic search: find chunks by meaning, using embeddings."""
import hashlib
from pathlib import Path

import numpy as np
import ollama

from app.ingest import Chunk

EMBEDDING_MODEL = "nomic-embed-text"
CACHE_FILE = Path(".cache/embeddings.npz")
BATCH_SIZE = 32


def embed_texts(texts: list[str]) -> np.ndarray:
    """Turn a list of texts into a matrix of vectors (one row per text)."""
    response = ollama.embed(model=EMBEDDING_MODEL, input=texts)
    return np.array(response["embeddings"])


def normalize(vectors: np.ndarray) -> np.ndarray:
    """Scale vectors to length 1, so that a dot product equals cosine similarity."""
    return vectors / np.linalg.norm(vectors, axis=-1, keepdims=True)


def text_key(text: str) -> str:
    """A unique fingerprint of a text (and of the model that embeds it)."""
    return hashlib.sha256(f"{EMBEDDING_MODEL}:{text}".encode("utf-8")).hexdigest()


def load_cache(path: Path = CACHE_FILE) -> dict[str, np.ndarray]:
    """Load saved embeddings from disk: {fingerprint: vector}."""
    if not path.exists():
        return {}
    data = np.load(path)
    return dict(zip(data["keys"], data["vectors"]))


def save_cache(cache: dict[str, np.ndarray], path: Path = CACHE_FILE) -> None:
    """Save embeddings to disk so we don't compute them again next time."""
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = list(cache)
    np.savez(path, keys=np.array(keys), vectors=np.array([cache[key] for key in keys]))


class SemanticIndex:
    """Stores the embedding of every chunk and finds the closest ones to a question."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        cache = load_cache()

        missing = [chunk for chunk in chunks if text_key(chunk.text) not in cache]
        if missing:
            print(f"Embedding {len(missing)} new chunks (saved for next time)...")
            for start in range(0, len(missing), BATCH_SIZE):
                batch = missing[start:start + BATCH_SIZE]
                vectors = embed_texts([f"search_document: {chunk.text}" for chunk in batch])
                for chunk, vector in zip(batch, vectors):
                    cache[text_key(chunk.text)] = vector
            save_cache(cache)

        self.vectors = normalize(np.array([cache[text_key(chunk.text)] for chunk in chunks]))

    def search(self, question: str, top_k: int = 3) -> list[Chunk]:
        """Return the `top_k` chunks whose meaning is closest to the question."""
        question_vector = normalize(embed_texts([f"search_query: {question}"])[0])
        scores = self.vectors @ question_vector
        best = np.argsort(scores)[::-1][:top_k]
        return [self.chunks[i] for i in best]