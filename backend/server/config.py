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
        self.ENVIRONMENT = os.getenv("CHATBOT_ENV", "development").strip().lower()
        if self.ENVIRONMENT not in {"development", "production"}:
            raise RuntimeError("CHATBOT_ENV must be either 'development' or 'production'.")
        self.IS_PRODUCTION = self.ENVIRONMENT == "production"

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

        # Production deployments perform migrations explicitly, after backup.
        # Development retains the existing automatic startup initialization.
        self.DATABASE_INITIALIZE_ON_START = os.getenv(
            "CHATBOT_DATABASE_INITIALIZE_ON_START",
            "false" if self.IS_PRODUCTION else "true",
        ).lower() == "true"
        self.DATABASE_BACKUP_CONFIRMED = os.getenv(
            "CHATBOT_DATABASE_BACKUP_CONFIRMED",
            "false",
        ).lower() == "true"

        # Flask session security
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SECURE = (
            os.getenv("CHATBOT_SESSION_COOKIE_SECURE", "false").lower() == "true"
        )
        self.SESSION_COOKIE_SAMESITE = "Lax"
        self.SESSION_COOKIE_NAME = "ctrl4_session"
        self.PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
        # The supported deployment is one application instance on one host.
        # Filesystem sessions keep payloads server-side and are not shared
        # across workers or hosts.
        self.SESSION_TYPE = os.getenv("CHATBOT_SESSION_TYPE", "cachelib")
        self.SESSION_CACHE_DIR = os.getenv(
            "CHATBOT_SESSION_FILE_DIR",
            str(DATA_DIR / "sessions"),
        )
        self.SESSION_CACHE_THRESHOLD = int(
            os.getenv("CHATBOT_SESSION_FILE_THRESHOLD", "500"),
        )
        self.SESSION_PERMANENT = True

        # Application logs contain operation metadata only. The default file is
        # intentionally outside tracked source paths and is rotated at runtime.
        self.LOG_LEVEL = os.getenv("CHATBOT_LOG_LEVEL", "INFO").upper()
        self._configured_log_file = os.getenv("CHATBOT_LOG_FILE", "").strip()
        self.LOG_FILE = self._configured_log_file or str(DATA_DIR / "logs" / "ctrl4.log")
        self.LOG_MAX_BYTES = int(os.getenv("CHATBOT_LOG_MAX_BYTES", str(5 * 1024 * 1024)))
        self.LOG_BACKUP_COUNT = int(os.getenv("CHATBOT_LOG_BACKUP_COUNT", "5"))

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
        self.RAG_DOCS_DIR = (
            os.getenv("CHATBOT_RAG_DOCS_DIR", "").strip()
            or str(AI_ENGINE_DIR / "knowledge_base")
        )
        self.RAG_INDEX_DIR = (
            os.getenv("CHATBOT_RAG_INDEX_DIR", "").strip()
            or str(DATA_DIR / "rag_index")
        )
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

        self._validate_production_configuration()

    def _validate_production_configuration(self) -> None:
        """Reject unsafe production startup while preserving development defaults."""
        if not self.IS_PRODUCTION:
            return

        validation_errors: list[str] = []
        if self.DEBUG:
            validation_errors.append("CHATBOT_DEBUG must be false in production.")
        if self.SECRET_KEY in {"", "dev-secret-key-change-me", "CHANGE_THIS_TO_A_SECURE_RANDOM_KEY"}:
            validation_errors.append("CHATBOT_SECRET_KEY must be a non-default value in production.")
        if not self.SESSION_COOKIE_SECURE:
            validation_errors.append("CHATBOT_SESSION_COOKIE_SECURE must be true in production.")
        if not os.getenv("CHATBOT_SESSION_FILE_DIR", "").strip():
            validation_errors.append("CHATBOT_SESSION_FILE_DIR must be configured in production.")
        if self.DATABASE_INITIALIZE_ON_START and not self.DATABASE_BACKUP_CONFIRMED:
            validation_errors.append(
                "CHATBOT_DATABASE_BACKUP_CONFIRMED must be true before production startup migrations."
            )
        if self.LOG_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            validation_errors.append("CHATBOT_LOG_LEVEL is invalid.")
        if not self._configured_log_file or not Path(self._configured_log_file).is_absolute():
            validation_errors.append(
                "CHATBOT_LOG_FILE must be an absolute configured path in production."
            )

        if validation_errors:
            raise RuntimeError(" ".join(validation_errors))
