"""Find the chunks that are most relevant to a question."""
import re

from app.ingest import Chunk

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "of", "to", "in", "on",
    "and", "or", "for", "with", "by", "as", "at", "from", "it", "this", "that",
    "what", "how", "why", "when", "which", "who", "does", "do", "can",
}


def tokenize(text: str) -> list[str]:
    """Lower-case the text, keep only words and drop very common words."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [word for word in words if word not in STOP_WORDS]


def keyword_search(question: str, chunks: list[Chunk], top_k: int = 3) -> list[Chunk]:
    """Return the `top_k` chunks that share the most words with the question."""
    question_words = set(tokenize(question))
    scored = []
    for chunk in chunks:
        score = sum(1 for word in tokenize(chunk.text) if word in question_words)
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [chunk for score, chunk in scored[:top_k]]