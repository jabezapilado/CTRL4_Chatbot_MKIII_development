"""
Service Registry

Initializes all AI services once during application startup.

CTRL4 Chatbot MK III

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from __future__ import annotations

import logging

from .emotion_service import EmotionService
from .language_service import LanguageService
from .rag_service import RAGService
from .prompt_builder import PromptBuilder
from .llm_service import LLMService
from .safety_service import SafetyService
from .intent_service import IntentService
from .topic_service import TopicService
from .metadata_service import MetadataExtractionService
from .response_safety_service import ResponseSafetyService
from .operational_guidance_service import OperationalGuidanceService
from .transient_chat_service import TransientChatService
from .ai_service import AIService
from .summary_service import SummaryService

logger = logging.getLogger(__name__)

logger.info("Initializing CTRL4 AI Services...")

try:

    # --------------------------------------------------
    # Core AI Services
    # --------------------------------------------------

    safety_service = SafetyService()
    emotion_service = EmotionService(safety=safety_service)
    language_service = LanguageService()
    rag_service = RAGService()
    prompt_builder = PromptBuilder()
    llm_service = LLMService()
    intent_service = IntentService()
    topic_service = TopicService()
    metadata_service = MetadataExtractionService()
    response_safety_service = ResponseSafetyService()
    operational_guidance_service = OperationalGuidanceService()
    transient_chat_service = TransientChatService()

    # --------------------------------------------------
    # Main AI Orchestrator
    # --------------------------------------------------

    ai_service = AIService(

        safety=safety_service,
        intent=intent_service,
        topic_classifier=topic_service,
        metadata_extractor=metadata_service,
        response_safety=response_safety_service,
        operational_guidance=operational_guidance_service,
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

    logger.info("CTRL4 AI Services initialized successfully.")

except Exception:
    logger.exception("Failed to initialize CTRL4 AI Services.")
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

        "version": "CTRL4 Chatbot MK III",

    }


__all__ = [
    "emotion_service",
    "language_service",
    "rag_service",
    "prompt_builder",
    "llm_service",
    "safety_service",
    "intent_service",
    "topic_service",
    "metadata_service",
    "response_safety_service",
    "operational_guidance_service",
    "transient_chat_service",
    "ai_service",
    "summary_service",
    "get_service_status",
]
