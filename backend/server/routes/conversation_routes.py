import logging
from flask import Blueprint, jsonify

from ..request_validation import require_role

from ..db import (
    fetch_rows,
    list_conversation_summaries,
)

logger = logging.getLogger(__name__)

conversation_bp = Blueprint(
    "conversation",
    __name__,
    url_prefix="/api",
)


@conversation_bp.get("/inquiries")
def inquiries():
    _, error = require_role("staff")
    if error:
        return error
    try:
        items = fetch_rows(
            "SELECT * FROM inquiries ORDER BY id DESC LIMIT 100"
        )
        return jsonify(
            {
                "success": True,
                "message": "Inquiries retrieved successfully.",
                "data": {
                    "items": items,
                },
            }
        ), 200
    except Exception:
        logger.exception("Failed to retrieve inquiries.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@conversation_bp.get("/conversation-summaries")
def conversation_summaries():
    _, error = require_role("staff")
    if error:
        return error
    try:
        items = list_conversation_summaries()
        return jsonify(
            {
                "success": True,
                "message": "Conversation summaries retrieved successfully.",
                "data": {
                    "items": items,
                },
            }
        ), 200
    except Exception:
        logger.exception("Failed to retrieve conversation summaries.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@conversation_bp.get("/escalations")
def escalations():
    _, error = require_role("staff")
    if error:
        return error
    try:
        items = fetch_rows(
            "SELECT * FROM escalations ORDER BY id DESC LIMIT 100"
        )
        return jsonify(
            {
                "success": True,
                "message": "Escalations retrieved successfully.",
                "data": {
                    "items": items,
                },
            }
        ), 200
    except Exception:
        logger.exception("Failed to retrieve escalations.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500