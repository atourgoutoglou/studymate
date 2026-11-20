"""Semantic search: find chunks by meaning, using embeddings."""
import numpy as np
import ollama

from app.ingest import Chunk

EMBEDDING_MODEL = "nomic-embed-text"


def embed_texts(texts: list[str]) -> np.ndarray:
    """Turn a list of texts into a matrix of vectors (one row per text)."""
    response = ollama.embed(model=EMBEDDING_MODEL, input=texts)
    return np.array(response["embeddings"])


def normalize(vectors: np.ndarray) -> np.ndarray:
    """Scale vectors to length 1, so that a dot product equals cosine similarity."""
    return vectors / np.linalg.norm(vectors, axis=-1, keepdims=True)

class SemanticIndex:
    """Stores the embedding of every chunk and finds the closest ones to a question."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        texts = [f"search_document: {chunk.text}" for chunk in chunks]
        self.vectors = normalize(embed_texts(texts))

    def search(self, question: str, top_k: int = 3) -> list[Chunk]:
        """Return the `top_k` chunks whose meaning is closest to the question."""
        question_vector = normalize(embed_texts([f"search_query: {question}"])[0])
        scores = self.vectors @ question_vector
        best = np.argsort(scores)[::-1][:top_k]
        return [self.chunks[i] for i in best]


if __name__ == "__main__":
    sentences = [
        "RAG combines a retriever with a text generator.",
        "Retrieval-augmented models look up documents before answering.",
        "My cat likes to sleep on the sofa.",
    ]
    question = "What is retrieval-augmented generation?"

    sentence_vectors = normalize(embed_texts([f"search_document: {s}" for s in sentences]))
    question_vector = normalize(embed_texts([f"search_query: {question}"])[0])
    print(f"Vector length: {len(question_vector)} numbers\n")

    for sentence, similarity in zip(sentences, sentence_vectors @ question_vector):
        print(f"{similarity:.3f}  {sentence}")