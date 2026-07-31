

from __future__ import annotations

from ..db import (
    current_time,
    save_conversation_summary,
    save_escalation,
)

from . import summary_service


def finalize_conversation(
    *,
    user: dict,
    conversation: list[dict],
    topic: str,
    language: str,
    emotion: str,
    flagged: bool,
) -> dict:
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
        save_escalation(
            {
                "account_id": user["id"],
                "summary_id": summary_id,
                "status": "pending",
                "created_at": current_time(),
            }
        )

    return {
        "success": True,
        "summary_id": summary_id,
    }