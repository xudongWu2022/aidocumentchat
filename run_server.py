#!/usr/bin/env python3
"""
RAG Document Chat Demo Script

This script starts the FastAPI server with the web UI.
Make sure you have set up your .env file with OPENAI_API_KEY and DATABASE_URL.
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_env():
    """Check if required environment variables are set"""
    required_vars = ['OPENAI_API_KEY', 'RAG_DATABASE_URL']
    missing = []

    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease set them in a .env file or environment variables.")
        print("Example .env file:")
        print("OPENAI_API_KEY=sk-your-key-here")
        print("RAG_DATABASE_URL=sqlite:///./rag_documents.db")
        return False

    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import openai
        import sqlalchemy
        import fitz  # PyMuPDF
        import docx
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def main():
    print("🚀 Starting RAG Document Chat Server...")

    if not check_env():
        sys.exit(1)

    if not check_dependencies():
        sys.exit(1)

    print("\n📋 Server Configuration:")
    print(f"   - API Key: {'*' * 20}...{os.getenv('OPENAI_API_KEY')[-4:] if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print(f"   - Database: {os.getenv('RAG_DATABASE_URL')}")
    print("   - Host: 0.0.0.0")
    print("   - Port: 8000")

    print("\n🌐 Web UI will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")

    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "api:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()