import logging

from flask import Blueprint, jsonify, request, session

from ..request_validation import require_login

from ..services import ai_service
from ..services.conversation_service import (
    determine_escalation_reason,
    finalize_conversation,
    record_chat_inquiry,
    should_escalate_conversation,
)

logger = logging.getLogger(__name__)

_ESCALATION_SESSION_KEY = "conversation_escalated"
_ESCALATION_REASON_SESSION_KEY = "conversation_escalation_reason"

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
            logger.warning("AIService returned an unsuccessful chat result.")
            return jsonify(
                {
                    "success": False,
                    "message": "Unable to generate a response.",
                    "data": {
                        "response": result.response,
                    },
                }
            ), 200

        record_chat_inquiry(
            account_id=user["id"],
            emotion=result.emotion,
            escalated=result.escalated,
        )

        should_escalate = should_escalate_conversation(
            escalated=result.escalated,
            normalized_emotion=result.normalized_emotion,
        )
        if should_escalate:
            session[_ESCALATION_SESSION_KEY] = True
            session[_ESCALATION_REASON_SESSION_KEY] = (
                determine_escalation_reason(
                    escalated=result.escalated,
                    normalized_emotion=result.normalized_emotion,
                )
                or "AI safety escalation."
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

    except Exception as exc:
        logger.error(
            "Chat request processing failed (exception_type=%s).",
            type(exc).__name__,
        )
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
            flagged=bool(session.get(_ESCALATION_SESSION_KEY)),
            escalation_reason=session.get(_ESCALATION_REASON_SESSION_KEY),
        )
        session.pop(_ESCALATION_SESSION_KEY, None)
        session.pop(_ESCALATION_REASON_SESSION_KEY, None)

        return jsonify(
            {
                "success": True,
                "message": "Conversation finalized successfully.",
                "data": result,
            }
        ), 200

    except Exception as exc:
        logger.error(
            "Conversation finalization failed (exception_type=%s).",
            type(exc).__name__,
        )

        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500
