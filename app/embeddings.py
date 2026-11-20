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