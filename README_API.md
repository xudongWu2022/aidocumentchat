# RAG Document QA API

This repository contains a simple Retrieval-Augmented Generation (RAG) agent and a minimal FastAPI server to upload text documents and ask grounded questions.

## Quick start

1. Install dependencies (recommended in a venv):

   pip install -r requirements.txt
   # or at minimum
   pip install fastapi uvicorn requests

2. Set environment variables in `.env` or your shell:

   OPENAI_API_KEY=sk-...
   DATABASE_URL=sqlite:///./data.db  # or your postgres URL

3. Run the app locally:

   uvicorn api:app --reload --host 0.0.0.0 --port 8000

## Endpoints

- POST /upload
  - Form fields:
    - `file` (file): plain text, PDF, or Word (.docx/.doc) file to upload
    - `doc_id` (optional string): document id (defaults to filename without extension)
  - Response: `{ "ingested": {"doc_id": <id>, "chunks_added": <n> }}`

- POST /ask
  - JSON body: `{ "doc_id": "mydoc", "question": "What is RAG?" }`
  - Response: `{ "answer": "...", "raw": { ... }}`

## Tests

- `python test_api.py` runs a small integration-style test using `TestClient` and a mocked OpenAI client. It demonstrates upload and ask workflows without calling external APIs.

## Notes & next improvements

- Currently only plain text uploads are supported; we can add PDF/Word parsing.
- Chunking and retrieval are basic; we can tune chunk size and add metadata filtering.
- For production, point `DATABASE_URL` to a persistent Postgres instance and secure the OpenAI key and API.
