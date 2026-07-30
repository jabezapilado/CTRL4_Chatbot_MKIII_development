from flask import Blueprint, jsonify

from ..auth import get_logged_in_user
from ..db import get_dashboard_stats

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard",
)


@dashboard_bp.get("/stats")
def dashboard_stats():
    user = get_logged_in_user()

    if not user:
        return jsonify({"error": "Login required."}), 401

    if str(user.get("role", "")).lower() != "staff":
        return jsonify({"error": "Staff access required."}), 403

    return jsonify(get_dashboard_stats()), 200
