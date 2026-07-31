import logging

from flask import Blueprint, jsonify, request

from ..request_validation import require_login

from ..db import (
    current_time,
    save_inquiry,
)

from ..services import ai_service
from ..services.conversation_service import finalize_conversation

logger = logging.getLogger(__name__)

CATEGORY_AI_CHAT = "ai_chat"

chatbot_bp = Blueprint(
    "chatbot",
    __name__,
)


@chatbot_bp.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}

    user = require_login()
    if not user:
        return jsonify(
            {
                "success": False,
                "message": "Login required.",
                "errors": None,
            }
        ), 401

    message = str(payload.get("message", "")).strip()

    if not message:
        return jsonify(
            {
                "success": False,
                "message": "Message is required.",
                "errors": None,
            }
        ), 400

    try:
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
            return jsonify(
                {
                    "success": False,
                    "message": "Unable to generate a response.",
                    "data": {
                        "response": result.response,
                    },
                }
            ), 200

        save_inquiry(
            {
                "account_id": user["id"] if user else None,
                "inquiry_type": CATEGORY_AI_CHAT,
                "emotion_result": result.emotion,
                "escalated": result.escalated,
                "appointment_recommended": False,
                "created_at": current_time(),
            }
        )

        return jsonify(
            {
                "success": True,
                "message": "Response generated successfully.",
                "data": {
                    "response": result.response,
                    "emotion": result.emotion,
                    "sentiment": result.sentiment,
                    "language": result.language,
                    "escalated": result.escalated,
                    "confidence": round(result.confidence, 4),
                },
            }
        ), 200

    except Exception:
        logger.exception("AIService failed while processing chat request.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@chatbot_bp.post("/chat/finalize")
def finalize_chat():
    payload = request.get_json(silent=True) or {}

    user = require_login()
    if not user:
        return jsonify(
            {
                "success": False,
                "message": "Login required.",
                "errors": None,
            }
        ), 401

    conversation = payload.get("conversation", [])

    if not conversation:
        return jsonify(
            {
                "success": False,
                "message": "Conversation is required.",
                "errors": None,
            }
        ), 400

    try:
        result = finalize_conversation(
            user=user,
            conversation=conversation,
            topic=str(payload.get("topic", "general")),
            language=str(payload.get("language", "unknown")),
            emotion=str(payload.get("emotion", "neutral")),
            flagged=bool(payload.get("flagged", False)),
        )

        return jsonify(
            {
                "success": True,
                "message": "Conversation finalized successfully.",
                "data": result,
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
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500
