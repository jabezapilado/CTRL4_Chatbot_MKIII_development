from flask import Blueprint, jsonify, request
import logging

from ..request_validation import require_role

from ..db import search_student_accounts

from ..services.account_service import (
    create_account_service,
    deactivate_admin_account_service,
    deactivate_staff_account_service,
    deactivate_student_account_service,
    list_accounts_service,
    update_admin_account_service,
    update_staff_account_service,
    update_student_account_service,
)

logger = logging.getLogger(__name__)

account_bp = Blueprint(
    "accounts",
    __name__,
    url_prefix="/api/accounts",
)


def _error_response(message: str, status: int):
    return jsonify(
        {
            "success": False,
            "message": message,
            "errors": None,
        }
    ), status


@account_bp.get("")
def accounts():
    _, error = require_role("admin")
    if error:
        return error
    try:
        items = list_accounts_service(request.args)
    except ValueError as exc:
        return _error_response(str(exc), 400)

    return jsonify(
        {
            "success": True,
            "message": "Accounts retrieved successfully.",
            "data": {"items": items},
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
        return _error_response(str(exc), 400)
    except FileExistsError as exc:
        return _error_response(str(exc), 409)
    except Exception:
        logger.exception("Failed to create account.")
        return _error_response("Internal server error.", 500)

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


@account_bp.patch("/admin/<int:account_id>")
def update_admin_account_route(account_id: int):
    user, error = require_role("admin")
    if error:
        return error

    payload = request.get_json(silent=True) or {}

    try:
        account = update_admin_account_service(account_id, payload)
    except ValueError as exc:
        return _error_response(str(exc), 400)
    except LookupError as exc:
        return _error_response(str(exc), 404)
    except FileExistsError as exc:
        return _error_response(str(exc), 409)
    except Exception:
        logger.exception("Failed to update administrator account.")
        return _error_response("Internal server error.", 500)

    logger.info(
        "Admin %s updated administrator account %s",
        user["id"],
        account["id"],
    )

    return jsonify(
        {
            "success": True,
            "message": "Administrator account updated successfully.",
            "data": {"account": account},
        }
    ), 200


@account_bp.delete("/admin/<int:account_id>")
def deactivate_admin_account_route(account_id: int):
    user, error = require_role("admin")
    if error:
        return error

    try:
        account = deactivate_admin_account_service(
            account_id,
            authenticated_admin_id=user["id"],
        )
    except ValueError as exc:
        return _error_response(str(exc), 400)
    except LookupError as exc:
        return _error_response(str(exc), 404)
    except Exception:
        logger.exception("Failed to deactivate administrator account.")
        return _error_response("Internal server error.", 500)

    logger.info(
        "Admin %s deactivated administrator account %s",
        user["id"],
        account["id"],
    )

    return jsonify(
        {
            "success": True,
            "message": "Administrator account deactivated successfully.",
            "data": {
                "id": account["id"],
                "status": account["status"],
            },
        }
    ), 200


@account_bp.patch("/staff/<int:account_id>")
def update_staff_account_route(account_id: int):
    user, error = require_role("admin")
    if error:
        return error

    payload = request.get_json(silent=True) or {}

    try:
        account = update_staff_account_service(account_id, payload)
    except ValueError as exc:
        return _error_response(str(exc), 400)
    except LookupError as exc:
        return _error_response(str(exc), 404)
    except FileExistsError as exc:
        return _error_response(str(exc), 409)
    except Exception:
        logger.exception("Failed to update staff account.")
        return _error_response("Internal server error.", 500)

    logger.info(
        "Admin %s updated staff account %s",
        user["id"],
        account["id"],
    )

    return jsonify(
        {
            "success": True,
            "message": "Staff account updated successfully.",
            "data": {"account": account},
        }
    ), 200


@account_bp.delete("/staff/<int:account_id>")
def deactivate_staff_account_route(account_id: int):
    user, error = require_role("admin")
    if error:
        return error

    try:
        account = deactivate_staff_account_service(account_id)
    except ValueError as exc:
        return _error_response(str(exc), 400)
    except LookupError as exc:
        return _error_response(str(exc), 404)
    except Exception:
        logger.exception("Failed to deactivate staff account.")
        return _error_response("Internal server error.", 500)

    logger.info(
        "Admin %s deactivated staff account %s",
        user["id"],
        account["id"],
    )

    return jsonify(
        {
            "success": True,
            "message": "Staff account deactivated successfully.",
            "data": {
                "id": account["id"],
                "status": account["status"],
            },
        }
    ), 200


@account_bp.patch("/<int:account_id>")
def update_account_route(account_id: int):
    user, error = require_role("admin")
    if error:
        return error

    payload = request.get_json(silent=True) or {}

    try:
        account = update_student_account_service(account_id, payload)
    except ValueError as exc:
        return _error_response(str(exc), 400)
    except LookupError as exc:
        return _error_response(str(exc), 404)
    except FileExistsError as exc:
        return _error_response(str(exc), 409)
    except Exception:
        logger.exception("Failed to update student account.")
        return _error_response("Internal server error.", 500)

    logger.info(
        "Admin %s updated student account %s",
        user["id"],
        account["id"],
    )

    return jsonify(
        {
            "success": True,
            "message": "Student account updated successfully.",
            "data": {"account": account},
        }
    ), 200


@account_bp.delete("/<int:account_id>")
def deactivate_account_route(account_id: int):
    user, error = require_role("admin")
    if error:
        return error

    try:
        account = deactivate_student_account_service(account_id)
    except ValueError as exc:
        return _error_response(str(exc), 400)
    except LookupError as exc:
        return _error_response(str(exc), 404)
    except Exception:
        logger.exception("Failed to deactivate student account.")
        return _error_response("Internal server error.", 500)

    logger.info(
        "Admin %s deactivated student account %s",
        user["id"],
        account["id"],
    )

    return jsonify(
        {
            "success": True,
            "message": "Student account deactivated successfully.",
            "data": {
                "id": account["id"],
                "status": account["status"],
            },
        }
    ), 200
