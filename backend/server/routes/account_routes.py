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
    _, error = require_role("admin")
    if error:
        return error
    return jsonify(
        {
            "success": True,
            "message": "Accounts retrieved successfully.",
            "data": {"items": list_accounts()},
        }
    ), 200


@account_bp.get("/search")
def search_accounts():
    user, error = require_role("staff")
    if error:
        return error

    query = str(request.args.get("q", "")).strip()

    if not query:
        return jsonify(
            {
                "success": True,
                "message": "No matching accounts.",
                "data": {"items": []},
            }
        ), 200

    return jsonify(
        {
            "success": True,
            "message": "Accounts retrieved successfully.",
            "data": {
                "items": search_student_accounts(query)
            },
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
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400
    except FileExistsError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 409
    except Exception:
        logger.exception("Failed to create account.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    logger.info(
        "Admin %s created account %s",
        user["id"],
        account["id"],
    )

    return jsonify(
        {
            "success": True,
            "message": "Account created successfully.",
            "data": {
                "id": account["id"],
                "status": "created",
                "student_number": account["student_number"],
                "staff_number": account["staff_number"],
            },
        }
    ), 201