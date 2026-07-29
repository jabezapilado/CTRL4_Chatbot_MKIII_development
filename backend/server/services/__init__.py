"""
Service Registry

Initializes all AI services once during application startup.

CTRL4 Chatbot MK II

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from __future__ import annotations

from .emotion_service import EmotionService
from .language_service import LanguageService
from .rag_service import RAGService
from .prompt_builder import PromptBuilder
from .llm_service import LLMService
from .safety_service import SafetyService
from .ai_service import AIService
from .summary_service import SummaryService

print("=" * 60)
print("Initializing CTRL4 AI Services...")
print("=" * 60)

try:

    # --------------------------------------------------
    # Core AI Services
    # --------------------------------------------------

    emotion_service = EmotionService()

    language_service = LanguageService()

    rag_service = RAGService()

    prompt_builder = PromptBuilder()

    llm_service = LLMService()

    safety_service = SafetyService()

    # --------------------------------------------------
    # Main AI Orchestrator
    # --------------------------------------------------

    ai_service = AIService(

        safety=safety_service,
        language=language_service,
        emotion=emotion_service,
        rag=rag_service,
        prompt_builder=prompt_builder,
        llm=llm_service,
    )
    # --------------------------------------------------
    # Conversation Summary Service
    # --------------------------------------------------

    summary_service = SummaryService(
        llm=llm_service,
    )

    print("CTRL4 AI Services initialized successfully.")

except Exception as exception:

    print("=" * 60)
    print("CTRL4 Initialization Error")
    print("=" * 60)
    print(exception)
    print("=" * 60)

    raise


def get_service_status() -> dict[str, object]:
    """
    Returns the initialization status of all AI services.
    Used by the health endpoint and debugging tools.
    """

    llm_status = llm_service.status()

    return {

        "status": (
            "healthy"
            if (
                emotion_service is not None
                and language_service is not None
                and rag_service.ready
                and llm_service is not None
                and safety_service is not None
                and ai_service is not None
                and summary_service is not None
            )
            else "degraded"
        ),

        "services": {

            "emotion": emotion_service is not None,

            "language": language_service is not None,

            "rag": rag_service.ready,

            "llm": llm_service is not None,

            "safety": safety_service is not None,

            "ai": ai_service is not None,
            
            "summary": summary_service is not None,

        },

        "models": {

            "emotion_model_loaded": emotion_service is not None,

            "rag_index_loaded": rag_service.ready,

            "llm_provider": llm_status.get("provider"),

            "llm_ready": llm_status.get("ready"),

            "llm_model": llm_status.get("model"),

        },

        "version": "CTRL4 Chatbot MK II",

    }


__all__ = [

    "emotion_service",

    "language_service",

    "rag_service",

    "prompt_builder",

    "llm_service",

    "safety_service",

    "ai_service",

    "summary_service",

    "get_service_status",
]