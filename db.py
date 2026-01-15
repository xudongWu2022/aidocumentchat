# db.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

# 使用专门的RAG数据库URL
RAG_DATABASE_URL = os.getenv("RAG_DATABASE_URL")
if not RAG_DATABASE_URL:
    raise RuntimeError("RAG_DATABASE_URL not set in .env")

engine = create_engine(RAG_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_db():
    return SessionLocal()


def test_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("[DB] Test query result:", result.scalar())
