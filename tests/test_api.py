from fastapi.testclient import TestClient

import app.api as api
from app.ingest import Chunk

client = TestClient(api.app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_empty_question_is_rejected():
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422


def test_ask_without_documents_returns_400(monkeypatch):
    monkeypatch.setattr(api.knowledge, "index", None)
    response = client.post("/ask", json={"question": "What is RAG?"})
    assert response.status_code == 400


def test_only_pdf_files_can_be_uploaded():
    response = client.post("/documents", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert response.status_code == 400


def test_ask_returns_answer_and_sources(monkeypatch):
    chunk = Chunk(source="notes.pdf", page=3, text="RAG combines retrieval and generation.")
    monkeypatch.setattr(api.knowledge, "chunks", [chunk])
    monkeypatch.setattr(api.knowledge, "index", object())  # any non-empty index
    monkeypatch.setattr(api, "hybrid_search", lambda question, chunks, index, top_k: [chunk])
    monkeypatch.setattr(api, "ask_llm", lambda question, context: "A fake answer [notes.pdf, page 3]")

    response = client.post("/ask", json={"question": "What is RAG?"})

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "A fake answer [notes.pdf, page 3]"
    assert data["sources"] == [
        {"file": "notes.pdf", "page": 3, "text": "RAG combines retrieval and generation."}
    ]