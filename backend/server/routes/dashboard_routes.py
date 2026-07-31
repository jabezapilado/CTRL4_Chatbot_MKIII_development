import logging
from flask import Blueprint, jsonify

from ..request_validation import require_role
from ..db import get_dashboard_stats

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard",
)


@dashboard_bp.get("/stats")
def dashboard_stats():
    user, error = require_role("staff")
    if error:
        return error

    try:
        stats = get_dashboard_stats()
        return jsonify(
            {
                "success": True,
                "message": "Dashboard statistics retrieved successfully.",
                "data": stats,
            }
        ), 200
    except Exception:
        logger.exception("Failed to retrieve dashboard statistics.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500
