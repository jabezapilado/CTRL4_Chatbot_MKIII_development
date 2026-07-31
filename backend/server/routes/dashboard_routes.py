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
        return jsonify(get_dashboard_stats()), 200
    except Exception:
        logger.exception("Failed to retrieve dashboard statistics.")
        return jsonify({"error": "Internal server error."}), 500
