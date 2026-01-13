from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import agent

app = FastAPI(title="RAG Document QA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    doc_id: str
    question: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile = File(...), doc_id: str | None = Form(None)):
    """Upload a plain text file and ingest it into the vector store."""
    if file.content_type not in ("text/plain", "text/csv", "application/octet-stream"):
        raise HTTPException(status_code=400, detail=f"Unsupported content type: {file.content_type}")

    body = await file.read()
    try:
        text = body.decode("utf-8")
    except Exception:
        # fallback: try latin-1
        text = body.decode("latin-1")

    if not doc_id:
        # fall back to filename without extension
        doc_id = (file.filename or "uploaded").rsplit(".", 1)[0]

    res = agent.ingest_document_text(doc_id, text)
    return {"ingested": res}


@app.post("/ask")
async def ask(req: AskRequest):
    """Ask a question grounded in a specific document (doc_id)."""
    out = agent.agent_executor(req.question, req.doc_id)
    # normalize output for API consumers
    if "answer" in out:
        return {"answer": out["answer"], "raw": out}
    return {"error": out}


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)