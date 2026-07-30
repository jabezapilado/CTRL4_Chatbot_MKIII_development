from flask import Blueprint, jsonify

from ..db import (
    fetch_rows,
    list_conversation_summaries,
)

conversation_bp = Blueprint(
    "conversation",
    __name__,
    url_prefix="/api",
)


@conversation_bp.get("/inquiries")
def inquiries():
    return jsonify(
        {
            "items": fetch_rows(
                "SELECT * FROM inquiries ORDER BY id DESC LIMIT 100"
            )
        }
    ), 200


@conversation_bp.get("/conversation-summaries")
def conversation_summaries():
    return jsonify(
        {
            "items": list_conversation_summaries(),
        }
    ), 200


@conversation_bp.get("/escalations")
def escalations():
    return jsonify(
        {
            "items": fetch_rows(
                "SELECT * FROM escalations ORDER BY id DESC LIMIT 100"
            )
        }
    ), 200