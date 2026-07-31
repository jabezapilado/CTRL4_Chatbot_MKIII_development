import logging
from flask import Blueprint, jsonify

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
    try:
        return jsonify(
            {
                "items": fetch_rows(
                    "SELECT * FROM inquiries ORDER BY id DESC LIMIT 100"
                )
            }
        ), 200
    except Exception:
        logger.exception("Failed to retrieve inquiries.")
        return jsonify({"error": "Internal server error."}), 500


@conversation_bp.get("/conversation-summaries")
def conversation_summaries():
    try:
        return jsonify(
            {
                "items": list_conversation_summaries(),
            }
        ), 200
    except Exception:
        logger.exception("Failed to retrieve conversation summaries.")
        return jsonify({"error": "Internal server error."}), 500


@conversation_bp.get("/escalations")
def escalations():
    try:
        return jsonify(
            {
                "items": fetch_rows(
                    "SELECT * FROM escalations ORDER BY id DESC LIMIT 100"
                )
            }
        ), 200
    except Exception:
        logger.exception("Failed to retrieve escalations.")
        return jsonify({"error": "Internal server error."}), 500