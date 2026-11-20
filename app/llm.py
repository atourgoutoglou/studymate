"""Communication with the local LLM (Ollama)."""
import ollama

MODEL = "llama3.2"

SYSTEM_PROMPT = (
    "You are StudyMate, a helpful study assistant. "
    "Answer ONLY using the context provided. "
    "After each fact, cite the page in brackets, e.g. [Page 3]. "
    "If the answer is not in the context, say: I could not find this in your documents."
)


def ask_llm(question: str, context: str = "") -> str:
    """Send a question (and optional context) to the LLM and return its answer."""
    if context:
        user_content = f"Context:\n{context}\n\nQuestion: {question}"
    else:
        user_content = question
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
    response = ollama.chat(model=MODEL, messages=messages)
    return response["message"]["content"]

if __name__ == "__main__":
    answer = ask_llm("In artificial intelligence, what is RAG? Answer in 2 sentences.")
    print(answer)