"""Communication with the local LLM (Ollama)."""
import ollama

MODEL = "llama3.1:8b"

SYSTEM_PROMPT = (
    "You are StudyMate, a helpful study assistant. "
    "Answer ONLY using the context provided. "
    "After each fact, cite the source in brackets, e.g. [rag_paper.pdf, page 3]. "
    "If the answer is not in the context, say: I could not find this in your documents."
)


def chat(system_prompt: str, user_message: str) -> str:
    """Send one system prompt and one user message to the LLM, return its reply."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    response = ollama.chat(model=MODEL, messages=messages)
    return response["message"]["content"]


def ask_llm(question: str, context: str = "") -> str:
    """Answer a question as StudyMate, using the given context."""
    if context:
        user_message = f"Context:\n{context}\n\nQuestion: {question}"
    else:
        user_message = question
    return chat(SYSTEM_PROMPT, user_message)