import os
import json
import pathlib

# Ensure DB env is set before importing agent (db.py reads it at import time)
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_agent.db")
os.environ.setdefault("OPENAI_API_KEY", "test")

import agent

# Mock client to avoid real OpenAI calls
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
    def __init__(self):
        self.call_count = 0

    class embeddings:
        @staticmethod
        def create(model, input):
            # deterministic small vector based on input length
            val = float(len(input) % 10)
            emb = [val for _ in range(8)]
            return MockEmbResp(emb)

    class chat:
        class completions:
            @staticmethod
            def create(**kwargs):
                # use a global-ish state stored on the MockClient instance; fallback to simple behavior
                # We'll detect by messages length/content whether to ask for a function call or return final answer.
                messages = kwargs.get("messages", [])
                # If no tool response yet, ask to call search_document
                has_tool_output = any(m.get("role") == "tool" for m in messages)
                if not has_tool_output:
                    # Use new tool_calls format
                    tool_calls = [{
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "search_document",
                            "arguments": json.dumps({"query": messages[-1]["content"], "doc_id": "sample", "top_k": 2})
                        }
                    }]
                    return MockResp({"tool_calls": tool_calls})
                else:
                    # extract tool output and summarize
                    tool_msg = next((m for m in messages if m.get("role") == "tool"), None)
                    content = tool_msg.get("content")
                    results = json.loads(content)
                    summary = " ".join([r["text"] for r in results])
                    answer = f"Answer (grounded): {summary}"
                    return MockResp({"content": answer})

# Replace the real client with the mock
agent.client = MockClient()

# Sample document
text = """
This is a sample document about RAG.

It explains that retrieval-augmented generation uses embeddings and search to ground LLM answers.

Key point: store chunks, compute embeddings, search by similarity.
"""

print("Ingesting sample document...")
res = agent.ingest_document_text("sample", text)
print("Ingest result:", res)

print("Running a semantic search for 'what is RAG'...")
search = agent.search_document("what is RAG", doc_id="sample", top_k=2)
print(json.dumps(search, indent=2, ensure_ascii=False))

print("Running agent_executor for a natural question...")
out = agent.agent_executor("What is RAG and how is it used?", doc_id="sample")
print("Agent output:")
print(json.dumps(out, indent=2, ensure_ascii=False))
