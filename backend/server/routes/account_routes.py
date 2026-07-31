from flask import Blueprint, jsonify, request
import logging

from ..request_validation import require_role

from ..db import (
    list_accounts,
    search_student_accounts,
)

from ..services.account_service import create_account_service

logger = logging.getLogger(__name__)

account_bp = Blueprint(
    "accounts",
    __name__,
    url_prefix="/api/accounts",
)

@account_bp.get("")
def accounts():
    return jsonify({"items": list_accounts()}), 200


@account_bp.get("/search")
def search_accounts():
    user, error = require_role("staff")
    if error:
        return error

    query = str(request.args.get("q", "")).strip()

    if not query:
        return jsonify({"items": []}), 200

    return jsonify(
        {
            "items": search_student_accounts(query)
        }
    ), 200


@account_bp.post("")
def create_account_route():
    user, error = require_role("admin")
    if error:
        return error

    payload = request.get_json(silent=True) or {}

    try:
        account = create_account_service(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except FileExistsError as exc:
        return jsonify({"error": str(exc)}), 409
    except Exception:
        logger.exception("Failed to create account.")
        return jsonify({"error": "Internal server error."}), 500

    logger.info(
        "Admin %s created account %s",
        user["id"],
        account["id"],
    )

    return jsonify(
        {
            "id": account["id"],
            "status": "created",
            "student_number": account["student_number"],
            "staff_number": account["staff_number"],
        }
    ), 201