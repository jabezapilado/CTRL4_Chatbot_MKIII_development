from __future__ import annotations

import logging

from flask import Blueprint, jsonify

from ..request_validation import require_any_role
from ..services.notification_service import (
    list_notifications_service,
    mark_notification_read_service,
)


logger = logging.getLogger(__name__)

notification_bp = Blueprint(
    "notifications",
    __name__,
    url_prefix="/api/notifications",
)


@notification_bp.get("")
def list_notifications_route():
    user, error = require_any_role("student", "staff")
    if error:
        return error

    try:
        items = list_notifications_service(user)
    except Exception:
        logger.exception("Failed to retrieve notifications.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    return jsonify(
        {
            "success": True,
            "message": "Notifications retrieved successfully.",
            "data": {"items": items},
        }
    ), 200


@notification_bp.patch("/<int:notification_id>/read")
def mark_notification_read_route(notification_id: int):
    user, error = require_any_role("student", "staff")
    if error:
        return error

    try:
        mark_notification_read_service(user, notification_id)
    except LookupError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 404
    except Exception:
        logger.exception("Failed to mark notification as read.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    return jsonify(
        {
            "success": True,
            "message": "Notification marked as read.",
            "data": {"status": "read"},
        }
    ), 200
