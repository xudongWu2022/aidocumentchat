import os
import json

# Ensure test DB and API env are set before importing agent/app
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_api.db")
os.environ.setdefault("OPENAI_API_KEY", "test")

import agent
from fastapi.testclient import TestClient
from api import app

# Use a mock client like in test_agent.py
class MockEmb:
    def __init__(self, emb):
        self.embedding = emb

class MockEmbResp:
    def __init__(self, emb):
        self.data = [MockEmb(emb)]

class MockChoice:
    def __init__(self, message):
        self.message = message

class MockResp:
    def __init__(self, message):
        self.choices = [MockChoice(message)]

class MockClient:
    class embeddings:
        @staticmethod
        def create(model, input):
            val = float(len(input) % 10)
            emb = [val for _ in range(8)]
            return MockEmbResp(emb)

    class chat:
        class completions:
            @staticmethod
            def create(**kwargs):
                messages = kwargs.get("messages", [])
                has_tool_output = any(m.get("role") == "tool" for m in messages)
                if not has_tool_output:
                    function_call = {
                        "name": "search_document",
                        "arguments": json.dumps({"query": messages[-1]["content"], "doc_id": "sample", "top_k": 2})
                    }
                    return MockResp({"function_call": function_call})
                else:
                    tool_msg = next((m for m in messages if m.get("role") == "tool"), None)
                    content = tool_msg.get("content")
                    results = json.loads(content)
                    summary = " ".join([r["text"] for r in results])
                    answer = f"Answer (grounded): {summary}"
                    return MockResp({"content": answer})

# Swap in the mock client
agent.client = MockClient()

client = TestClient(app)

# Upload sample file
sample_text = """
FastAPI test document about RAG.

RAG combines retrieval with generation.
"""
files = {"file": ("sample.txt", sample_text, "text/plain")}
res = client.post("/upload", files=files, data={"doc_id": "apidoc"})
print("Upload status", res.status_code, res.json())

# Test PDF upload (mock - since we can't create real PDF in test)
# In real usage, you'd upload an actual PDF file
print("Note: PDF/Word upload supported - test with real files")

# Ask a question
res2 = client.post("/ask", json={"doc_id": "apidoc", "question": "What is RAG?"})
print("Ask status", res2.status_code, res2.json())
