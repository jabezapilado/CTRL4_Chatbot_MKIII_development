from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from datetime import timedelta

from typing import Final


BASE_DIR: Final = Path(__file__).resolve().parents[1]
PROJECT_ROOT: Final = BASE_DIR.parent
AI_ENGINE_DIR: Final = PROJECT_ROOT / "ai_engine"
DATA_DIR: Final = BASE_DIR / "data"
load_dotenv(BASE_DIR / ".env")
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    def __init__(self) -> None:
        self.DB_HOST = os.getenv("CHATBOT_DB_HOST", "127.0.0.1")
        self.DB_PORT = int(os.getenv("CHATBOT_DB_PORT", "3306"))
        self.DB_USER = os.getenv("CHATBOT_DB_USER", "root")
        self.DB_PASSWORD = os.getenv("CHATBOT_DB_PASSWORD", "")
        self.DB_NAME = os.getenv("CHATBOT_DB_NAME", "soc_chatbot")
        self.DB_CHARSET = os.getenv("CHATBOT_DB_CHARSET", "utf8mb4")
        self.DB_SSL_CA = os.getenv("CHATBOT_DB_SSL_CA", "")
        self.DB_SSL_VERIFY_CERT = os.getenv("CHATBOT_DB_SSL_VERIFY_CERT", "false").lower() == "true"
        self.DEBUG = os.getenv("CHATBOT_DEBUG", "true").lower() == "true"
        self.SECRET_KEY = os.getenv("CHATBOT_SECRET_KEY", "dev-secret-key-change-me")
        self.PORT = int(os.getenv("CHATBOT_PORT", "5001"))

        # Flask session security
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SECURE = (
            os.getenv("CHATBOT_SESSION_COOKIE_SECURE", "false").lower() == "true"
        )
        self.SESSION_COOKIE_SAMESITE = "Lax"
        self.SESSION_COOKIE_NAME = "ctrl4_session"
        self.PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

        self.SEED_STUDENT_EMAIL = os.getenv("CHATBOT_SEED_STUDENT_EMAIL", "student@hau.edu.ph")
        self.SEED_STUDENT_NAME = os.getenv("CHATBOT_SEED_STUDENT_NAME", "Maria Santos")
        self.SEED_STUDENT_PASSWORD = os.getenv("CHATBOT_SEED_STUDENT_PASSWORD", "")
        self.SEED_STUDENT_NUMBER = os.getenv("CHATBOT_SEED_STUDENT_NUMBER", "2024-00001")
        self.SEED_STUDENT_GENDER = os.getenv("CHATBOT_SEED_STUDENT_GENDER", "Female")
        self.SEED_STUDENT_PROGRAM = os.getenv("CHATBOT_SEED_STUDENT_PROGRAM", "BS Computer Science")
        
        self.SEED_STUDENT2_EMAIL = os.getenv("CHATBOT_SEED_STUDENT2_EMAIL", "student2@hau.edu.ph")
        self.SEED_STUDENT2_NAME = os.getenv("CHATBOT_SEED_STUDENT2_NAME", "Juan Dela Cruz")
        self.SEED_STUDENT2_PASSWORD = os.getenv("CHATBOT_SEED_STUDENT2_PASSWORD", "")        
        self.SEED_STUDENT2_NUMBER = os.getenv("CHATBOT_SEED_STUDENT2_NUMBER", "2024-00002")
        self.SEED_STUDENT2_GENDER = os.getenv("CHATBOT_SEED_STUDENT2_GENDER", "Male")
        self.SEED_STUDENT2_PROGRAM = os.getenv("CHATBOT_SEED_STUDENT2_PROGRAM", "BS Information Technology - Web Development")

        self.SEED_STAFF_EMAIL = os.getenv("CHATBOT_SEED_STAFF_EMAIL", "ryan@hau.edu.ph")
        self.SEED_STAFF_NAME = os.getenv("CHATBOT_SEED_STAFF_NAME", "Ryan Tibe")
        self.SEED_STAFF_PASSWORD = os.getenv("CHATBOT_SEED_STAFF_PASSWORD", "")
        self.SEED_STAFF_NUMBER = os.getenv("CHATBOT_SEED_STAFF_NUMBER", "STF-0001")
        self.SEED_STAFF_GENDER = os.getenv("CHATBOT_SEED_STAFF_GENDER", "Male")
        
        self.SEED_STAFF2_EMAIL = os.getenv("CHATBOT_SEED_STAFF2_EMAIL", "hannah@hau.edu.ph")
        self.SEED_STAFF2_NAME = os.getenv("CHATBOT_SEED_STAFF2_NAME", "Hannah Lei Alvarado")
        self.SEED_STAFF2_PASSWORD = os.getenv("CHATBOT_SEED_STAFF2_PASSWORD", "")
        self.SEED_STAFF2_NUMBER = os.getenv("CHATBOT_SEED_STAFF2_NUMBER", "STF-0002")
        self.SEED_STAFF2_GENDER = os.getenv("CHATBOT_SEED_STAFF2_GENDER", "Female")

        self.SEED_ADMIN_EMAIL = os.getenv("CHATBOT_SEED_ADMIN_EMAIL", "admin@hau.edu.ph")
        self.SEED_ADMIN_NAME = os.getenv("CHATBOT_SEED_ADMIN_NAME", "System Admin")
        self.SEED_ADMIN_PASSWORD = os.getenv("CHATBOT_SEED_ADMIN_PASSWORD", "")
        self.SEED_ADMIN_GENDER = os.getenv("CHATBOT_SEED_ADMIN_GENDER", "Prefer not to say")
        
        # Supported academic programs
        self.PROGRAMS: Final[tuple[str, ...]] = (
            "BS Computer Science",
            "BS Information Technology - Web Development",
            "BS Information Technology - Network Administration",
            "BS Cybersecurity",
            "BS EMC - Digital Animation",
        )

        # Staff number generation
        self.STAFF_NUMBER_PREFIX = "STF"
        self.STAFF_NUMBER_PADDING = 4
        self.STAFF_NUMBER_SEPARATOR = "-"
        
        # Student number generation
        self.STUDENT_NUMBER_PADDING = 5
        self.STUDENT_NUMBER_SEPARATOR = "-"
        
        
        # Multilingual RAG configuration
        self.RAG_DOCS_DIR = os.getenv("CHATBOT_RAG_DOCS_DIR", str(AI_ENGINE_DIR / "knowledge_base"))
        self.RAG_INDEX_DIR = os.getenv("CHATBOT_RAG_INDEX_DIR", str(DATA_DIR / "rag_index"))
        self.RAG_EMBEDDING_MODEL = os.getenv("CHATBOT_RAG_EMBEDDING_MODEL", "intfloat/multilingual-e5-large")
        self.RAG_TOP_K = int(os.getenv("CHATBOT_RAG_TOP_K", "5"))
        self.RAG_MIN_SCORE = float(os.getenv("CHATBOT_RAG_MIN_SCORE", "0.30"))
        self.RAG_CHUNK_SIZE = int(os.getenv("CHATBOT_RAG_CHUNK_SIZE", "700"))
        self.RAG_CHUNK_OVERLAP = int(os.getenv("CHATBOT_RAG_CHUNK_OVERLAP", "120"))
        self.RAG_AUTO_BUILD_ON_START = os.getenv("CHATBOT_RAG_AUTO_BUILD_ON_START", "true").lower() == "true"
        self.RAG_GENERATOR_MODEL = os.getenv("CHATBOT_RAG_GENERATOR_MODEL", "")

        # Gemini configuration
        self.GEMINI_API_KEY = os.getenv(
            "CHATBOT_GEMINI_API_KEY",
            ""
        )

        self.GEMINI_MODEL = os.getenv(
            "CHATBOT_GEMINI_MODEL",
            "gemini-2.5-flash"
        )

        self.GEMINI_TEMPERATURE = float(
            os.getenv(
                "CHATBOT_GEMINI_TEMPERATURE",
                "0.7"
            )
        )

        self.GEMINI_MAX_OUTPUT_TOKENS = int(
            os.getenv(
                "CHATBOT_GEMINI_MAX_OUTPUT_TOKENS",
                "1024"
            )
        )
        
        # LLM configuration
        self.LLM_PROVIDER = os.getenv(
            "CHATBOT_LLM_PROVIDER",
            "ollama"
        )

        self.OLLAMA_URL = os.getenv(
            "CHATBOT_OLLAMA_URL",
            "http://localhost:11434/api/generate"
        )

        self.OLLAMA_MODEL = os.getenv(
            "CHATBOT_OLLAMA_MODEL",
            "qwen2.5:7b"
        )
        
        # Emotion-based escalation configuration
        self.EMOTION_ESCALATION_ENABLED = os.getenv("CHATBOT_EMOTION_ESCALATION_ENABLED", "true").lower() == "true"
        self.EMOTION_ESCALATION_THRESHOLD = float(os.getenv("CHATBOT_EMOTION_ESCALATION_THRESHOLD", "0.55"))