from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
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
    """Upload a plain text, PDF, or Word file and ingest it into the vector store."""
    supported_types = {
        "text/plain": ".txt",
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/msword": ".doc",
        "application/octet-stream": None  # fallback for files without proper MIME
    }

    if file.content_type not in supported_types:
        raise HTTPException(status_code=400, detail=f"Unsupported content type: {file.content_type}. Supported: {', '.join(supported_types.keys())}")

    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        if not doc_id:
            # fall back to filename without extension
            doc_id = (file.filename or "uploaded").rsplit(".", 1)[0]

        res = agent.ingest_document_file(temp_path, doc_id)
        return {"ingested": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


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