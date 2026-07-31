from flask import Blueprint, jsonify, request

from ..auth import get_logged_in_user

from ..db import (
    list_accounts,
    search_student_accounts,
)

from ..services.account_service import create_account_service

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
    user = get_logged_in_user()

    if not user or str(user.get("role", "")).lower() != "staff":
        return jsonify({"error": "Staff access required."}), 403

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
    user = get_logged_in_user()

    if not user or str(user.get("role", "")).lower() != "admin":
        return jsonify({"error": "Administrator access required."}), 403

    payload = request.get_json(silent=True) or {}

    try:
        account = create_account_service(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except FileExistsError as exc:
        return jsonify({"error": str(exc)}), 409

    return jsonify(
        {
            "id": account["id"],
            "status": "created",
            "student_number": account["student_number"],
            "staff_number": account["staff_number"],
        }
    ), 201