from __future__ import annotations

import logging
from typing import Final

from ..db import (
    current_time,
    save_conversation_summary,
    save_escalation,
)

from . import summary_service

logger = logging.getLogger(__name__)

ESCALATION_PENDING: Final[str] = "pending"


def _save_escalation(summary_id: int, account_id: int) -> None:
    save_escalation(
        {
            "account_id": account_id,
            "summary_id": summary_id,
            "status": ESCALATION_PENDING,
            "created_at": current_time(),
        }
    )


def finalize_conversation(
    *,
    user: dict,
    conversation: list[dict],
    topic: str,
    language: str,
    emotion: str,
    flagged: bool,
) -> dict:
    logger.info(
        "Finalizing conversation for account_id=%s flagged=%s",
        user["id"],
        flagged,
    )
    summary = summary_service.generate_summary(
        student_name=user["full_name"],
        conversation=conversation,
        topic=topic,
        language=language,
        emotion=emotion,
        flagged=flagged,
    )

    summary_id = save_conversation_summary(
        {
            "account_id": user["id"],
            "primary_concern": summary.primary_concern,
            "conversation_type": summary.conversation_type,
            "emotion_results": summary.emotion,
            "flagged_status": summary.flagged,
            "appointment_recommendation": summary.appointment_recommendation,
            "recommendations": summary.recommendations,
            "suggested_intervention": summary.suggested_intervention,
            "language_used": summary.language,
            "total_messages": summary.total_messages,
            "summary": summary.summary,
            "created_at": current_time(),
        }
    )

    if summary.flagged:
        _save_escalation(summary_id, user["id"])

    logger.info(
        "Conversation finalized successfully. summary_id=%s",
        summary_id,
    )

    return {
        "success": True,
        "summary_id": summary_id,
    }