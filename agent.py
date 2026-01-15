import os
import json
import math
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

from tools_schema import TOOLS
from db import engine, get_db

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

SYSTEM_PROMPT = """
You are a document QA agent. Your job is:
1) Decide when to search the document.
2) Use the `search_document` tool to retrieve relevant passages.
3) Then answer the user's question based ONLY on the retrieved context.
4) If you need more context, call the tool again.
5) When you are ready, give a concise, grounded answer.

Always prefer using the tool instead of guessing from your own knowledge.
If you call the `search_document` tool, pass a JSON object with the `query`, an optional `doc_id`, and `top_k`.
"""


def call_llm(messages, tools=TOOLS, tool_choice="auto"):
    kwargs = {
        "model": OPENAI_MODEL,
        "messages": messages,
    }

    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = tool_choice

    return client.chat.completions.create(**kwargs)


# --- DB / indexing helpers -------------------------------------------------

from sqlalchemy import text as sa_text

def create_tables():
    # create a simple table to hold text chunks and embeddings
    with engine.begin() as conn:
        conn.execute(
            sa_text(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id TEXT NOT NULL,
                    chunk_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    embedding TEXT NOT NULL
                )
                """
            )
        )


def _chunk_text(text: str, max_chars: int = 1000, overlap: int = 200) -> List[str]:
    # naive splitter by paragraphs and fixed-width sliding window
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []

    for p in paragraphs:
        if len(p) <= max_chars:
            chunks.append(p)
            continue
        # sliding window
        start = 0
        while start < len(p):
            end = start + max_chars
            chunks.append(p[start:end].strip())
            if end >= len(p):
                break
            start = end - overlap
    return chunks


def _extract_text_from_file(file_path: str) -> str:
    """Extract text from various file types."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext == '.pdf':
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except ImportError:
            raise ImportError("PyMuPDF is required for PDF files. Install with: pip install PyMuPDF")
    elif ext in ['.docx', '.doc']:
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except ImportError:
            raise ImportError("python-docx is required for Word files. Install with: pip install python-docx")
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: .txt, .pdf, .docx, .doc")


def ingest_document_text(doc_id: str, text: str):
    """Split the document, compute embeddings and store chunks in DB."""
    try:
        create_tables()
        chunks = _chunk_text(text)
        inserted = 0

        for i, c in enumerate(chunks):
            # create embedding
            resp = client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=c)
            emb = resp.data[0].embedding
            # store as JSON
            with engine.begin() as conn:
                conn.execute(
                    sa_text("INSERT INTO chunks (doc_id, chunk_id, text, embedding) VALUES (:doc_id, :chunk_id, :text, :embedding)"),
                    {"doc_id": doc_id, "chunk_id": f"{doc_id}_chunk_{i}", "text": c, "embedding": json.dumps(emb)},
                )
            inserted += 1

        return {"doc_id": doc_id, "chunks_added": inserted}
    except Exception as e:
        print(f"Error in ingest_document_text: {e}")
        raise


def ingest_document_file(path: str, doc_id: str = None):
    if not doc_id:
        doc_id = os.path.splitext(os.path.basename(path))[0]
    text = _extract_text_from_file(path)
    return ingest_document_text(doc_id, text)


# --- semantic search ------------------------------------------------------

def _cosine_similarity(a: List[float], b: List[float]) -> float:
    # small, pure-Python cosine similarity
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def search_document(query: str, doc_id: str = "doc1", top_k: int = 3) -> List[Dict]:
    """Tool function used by the LLM. Returns `top_k` relevant chunks for `query` in `doc_id`."""
    # compute query embedding
    q_resp = client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=query)
    q_emb = q_resp.data[0].embedding

    # fetch all chunks for doc_id
    with engine.connect() as conn:
        rows = conn.execute(
            sa_text("SELECT chunk_id, text, embedding FROM chunks WHERE doc_id = :doc_id"),
            {"doc_id": doc_id}
        ).fetchall()

    candidates = []
    for r in rows:
        chunk_id, text, emb_json = r
        try:
            emb = json.loads(emb_json)
        except Exception:
            continue
        score = _cosine_similarity(q_emb, emb)
        candidates.append({"chunk_id": chunk_id, "text": text, "score": score})

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:max(0, int(top_k))]


# --- agent executor (supports tool-calls) --------------------------------

def agent_executor(user_question: str, doc_id: str = "doc1") -> Dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_question}
    ]

    max_rounds = 4
    for _round in range(max_rounds):
        resp = call_llm(messages)
        choice = resp.choices[0]
        msg = choice.message

        # (1) If model decided to call a tool (function-call style), detect it
        tool_name = None
        tool_args = None
        tool_calls = None

        # attempt multiple detection strategies (dict-like or attribute-like)
        try:
            # dict-like
            m = msg if isinstance(msg, dict) else msg.__dict__
            tc = m.get("tool_calls")
            if tc:
                # 处理tool_calls数组（新版本OpenAI）
                if isinstance(tc, list) and len(tc) > 0:
                    tool_call = tc[0]
                    tool_name = tool_call.get("function", {}).get("name")
                    args = tool_call.get("function", {}).get("arguments")
                    tool_calls = tc  # 保存完整的tool_calls
                    if isinstance(args, str):
                        try:
                            tool_args = json.loads(args)
                        except Exception:
                            tool_args = {}
                    else:
                        tool_args = args or {}
        except Exception:
            pass

        # fallback: some SDKs put function call on message.tool_calls attr
        if not tool_name:
            tc_attr = getattr(msg, "tool_calls", None)
            if tc_attr:
                if isinstance(tc_attr, list) and len(tc_attr) > 0:
                    tool_call = tc_attr[0]
                    tool_name = getattr(tool_call.function, "name", None) if hasattr(tool_call, "function") else None
                    args = getattr(tool_call.function, "arguments", None) if hasattr(tool_call, "function") else None
                    tool_calls = tc_attr  # 保存完整的tool_calls
                    if isinstance(args, str):
                        try:
                            tool_args = json.loads(args)
                        except Exception:
                            tool_args = {}
                    else:
                        tool_args = args or {}

        # (2) If a tool call was requested, run it and append tool result to messages
        if tool_name:
            print(f"[agent] Model requested tool: {tool_name} with args {tool_args}")

            # First, add the assistant message with tool_calls to the conversation
            assistant_content = None
            if isinstance(msg, dict):
                assistant_content = msg.get("content")
            else:
                assistant_content = getattr(msg, "content", None)

            assistant_msg = {
                "role": "assistant",
                "content": assistant_content,
                "tool_calls": tool_calls
            }
            messages.append(assistant_msg)

            if tool_name == "search_document":
                q = tool_args.get("query") if tool_args else user_question
                top_k = int(tool_args.get("top_k", 3)) if tool_args else 3
                d_id = tool_args.get("doc_id", doc_id) if tool_args else doc_id
                result = search_document(q, d_id, top_k)
                # attach the tool output as a tool message for the model
                # Get tool_call_id from the first tool call
                tool_call_id = "call_1"
                if tool_calls and len(tool_calls) > 0:
                    if isinstance(tool_calls[0], dict):
                        tool_call_id = tool_calls[0].get("id", "call_1")
                    else:
                        # ChatCompletionMessageToolCall object
                        tool_call_id = getattr(tool_calls[0], "id", "call_1")

                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_name,
                    "content": json.dumps(result)
                }
                messages.append(tool_msg)
                continue  # ask the model again with the tool output in context
            else:
                # unknown tool - send a message back
                # Get tool_call_id from the first tool call
                tool_call_id = "call_1"
                if tool_calls and len(tool_calls) > 0:
                    if isinstance(tool_calls[0], dict):
                        tool_call_id = tool_calls[0].get("id", "call_1")
                    else:
                        # ChatCompletionMessageToolCall object
                        tool_call_id = getattr(tool_calls[0], "id", "call_1")

                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_name,
                    "content": json.dumps({"error": "unknown tool"})
                }
                messages.append(tool_msg)
                continue

        # (3) No tool requested -> treat as final assistant response
        assistant_content = None
        if isinstance(msg, dict):
            assistant_content = msg.get("content")
        else:
            assistant_content = getattr(msg, "content", None)

        if assistant_content:
            # Add the final assistant message to the conversation
            final_msg = {
                "role": "assistant",
                "content": assistant_content
            }
            messages.append(final_msg)

            # return the assistant message
            print("[agent] Final answer from model:")
            print(assistant_content)
            return {"answer": assistant_content}

    # if we exit loop without a final content
    return {"error": "No final answer after max rounds"}


# --- simple CLI for manual testing ---------------------------------------
if __name__ == "__main__":
    print("Simple RAG agent CLI. Commands:\n  ingest <file_path> [doc_id]\n  ask <doc_id> <question>\n  exit")
    while True:
        raw = input("cmd> ").strip()
        if not raw:
            continue
        parts = raw.split(maxsplit=2)
        cmd = parts[0]
        if cmd == "exit":
            break
        if cmd == "ingest":
            if len(parts) < 2:
                print("usage: ingest <file_path> [doc_id]")
                continue
            path = parts[1]
            doc_id = parts[2] if len(parts) > 2 else None
            res = ingest_document_file(path, doc_id)
            print("Ingested:", res)
            continue
        if cmd == "ask":
            if len(parts) < 3:
                print("usage: ask <doc_id> <question>")
                continue
            doc_id = parts[1]
            question = parts[2]
            print("Asking...")
            out = agent_executor(question, doc_id)
            print(out.get("answer") or out)
            continue
        print("Unknown command")
    