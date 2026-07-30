import logging

from flask import Blueprint, jsonify, request

from ..auth import get_logged_in_user

from ..db import (
    current_time,
    save_conversation_summary,
    save_escalation,
    save_inquiry,
)

from ..services import (
    ai_service,
    summary_service,
)

logger = logging.getLogger(__name__)

CATEGORY_AI_CHAT = "ai_chat"

chatbot_bp = Blueprint(
    "chatbot",
    __name__,
)


@chatbot_bp.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required."}), 400

    result = ai_service.respond(

        message=message,

        conversation=payload.get(
            "conversation",
            [],
        ),

    )
    
    logger.info(
        "AI response generated (emotion=%s, language=%s, escalated=%s, confidence=%.4f)",
        result.emotion,
        result.language,
        result.escalated,
        result.confidence,
    )
    
    if not result.success:

        logger.warning(
            "AIService failed for message: %s",
            message,
        )

        return jsonify({

            "success": False,

            "response": result.response,

        }), 200

    inquiry_id = save_inquiry(
        {
            "account_id": get_logged_in_user()["id"],
            "inquiry_type": CATEGORY_AI_CHAT,
            "emotion_result": result.emotion,
            "escalated": result.escalated,
            "appointment_recommended": False,
            "created_at": current_time(),
        }
    )


    return jsonify({

        "success": result.success,

        "response": result.response,

        "emotion": result.emotion,

        "sentiment": result.sentiment,

        "language": result.language,

        "escalated": result.escalated,

        "confidence": round(
            result.confidence,
            4,
        ),

    }), 200
    
@chatbot_bp.post("/chat/finalize")
def finalize_chat():
    payload = request.get_json(silent=True) or {}

    conversation = payload.get("conversation", [])

    if not conversation:
        return jsonify({"error": "Conversation is required."}), 400

    user = get_logged_in_user()

    if not user:
        return jsonify({"error": "Login required."}), 401

    try:
        summary = summary_service.generate_summary(
            student_name=user["full_name"],
            conversation=conversation,
            topic=str(payload.get("topic", "general")),
            language=str(payload.get("language", "unknown")),
            emotion=str(payload.get("emotion", "neutral")),
            flagged=bool(payload.get("flagged", False)),
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

        return jsonify(
            {
                "success": True,
                "summary_id": summary_id,
            }
        ), 200

    except Exception:
        logger.exception(
            "Failed to finalize conversation for user %s.",
            user["id"],
        )

        return jsonify(
            {
                "success": False,
                "error": "Unable to finalize conversation.",
            }
        ), 500 
