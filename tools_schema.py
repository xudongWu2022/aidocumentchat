# tools_schema.py
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_document",
            "description": "Search the internal document for relevant passages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user question or sub-question to search for."
                    },
                    "doc_id": {
                        "type": "string",
                        "description": "Document ID to search in.",
                        "default": "doc1"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "How many relevant chunks to return.",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        }
    }
]
