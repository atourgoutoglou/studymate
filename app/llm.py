"""Communication with the local LLM (Ollama)."""
import ollama

MODEL = "llama3.2"

SYSTEM_PROMPT = (
    "You are StudyMate, a helpful study assistant. "
    "Answer clearly and concisely."
)


def ask_llm(question: str) -> str:
    """Send a question to the LLM and return its answer."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    response = ollama.chat(model=MODEL, messages=messages)
    return response["message"]["content"]


if __name__ == "__main__":
    answer = ask_llm("In artificial intelligence, what is RAG? Answer in 2 sentences.")
    print(answer)