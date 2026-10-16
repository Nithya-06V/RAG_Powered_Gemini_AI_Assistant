import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "local-development-key-change-before-deployment")
    DATABASE_PATH = Path(os.getenv("DATABASE_PATH", BASE_DIR / "instance" / "app.db"))
    UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", BASE_DIR / "uploads"))
    VECTOR_STORE_PATH = Path(os.getenv("VECTOR_STORE_PATH", BASE_DIR / "vector_store"))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
    GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001").strip()
    DEMO_USERNAME = os.getenv("DEMO_USERNAME", "admin")
    DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "admin123")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
