"""StudyMate REST API.  Run with:  uvicorn app.api:app --reload"""
from collections import Counter
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.embeddings import SemanticIndex
from app.hybrid import hybrid_search
from app.ingest import Chunk, chunk_folder
from app.llm import ask_llm
from app.main import build_context

DATA_FOLDER = Path("data")


# ---------- Data models (what goes in and out of the API) ----------
class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class Source(BaseModel):
    file: str
    page: int
    text: str


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


class DocumentInfo(BaseModel):
    name: str
    chunks: int


# ---------- The knowledge base: all PDFs + search index, kept in memory ----------
class KnowledgeBase:
    def __init__(self, folder: Path):
        self.folder = folder
        self.chunks: list[Chunk] = []
        self.index: SemanticIndex | None = None

    def reload(self) -> None:
        """Read all PDFs again and rebuild the search index."""
        self.folder.mkdir(exist_ok=True)
        self.chunks = chunk_folder(self.folder)
        self.index = SemanticIndex(self.chunks) if self.chunks else None

    def documents(self) -> list[DocumentInfo]:
        """One entry per PDF, with how many chunks it has."""
        counts = Counter(chunk.source for chunk in self.chunks)
        return [DocumentInfo(name=name, chunks=count) for name, count in sorted(counts.items())]


knowledge = KnowledgeBase(DATA_FOLDER)


@asynccontextmanager
async def lifespan(app: FastAPI):
    knowledge.reload()  # runs once, when the server starts
    yield


app = FastAPI(title="StudyMate API", lifespan=lifespan)


# ---------- Endpoints ----------
@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/documents")
def list_documents() -> list[DocumentInfo]:
    return knowledge.documents()


@app.post("/documents", status_code=201)
def upload_document(file: UploadFile) -> list[DocumentInfo]:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    target = DATA_FOLDER / Path(file.filename).name  # .name blocks paths like "../../x.pdf"
    target.write_bytes(file.file.read())
    knowledge.reload()
    return knowledge.documents()


@app.post("/ask")
def ask(request: AskRequest) -> AskResponse:
    if knowledge.index is None:
        raise HTTPException(status_code=400, detail="Upload a PDF first.")

    relevant = hybrid_search(request.question, knowledge.chunks, knowledge.index, top_k=5)
    answer = ask_llm(request.question, context=build_context(relevant))
    sources = [Source(file=chunk.source, page=chunk.page, text=chunk.text) for chunk in relevant]
    return AskResponse(answer=answer, sources=sources)