import logging
from flask import Blueprint, jsonify, request

from ..db import load_settings, save_settings
from ..request_validation import require_role

logger = logging.getLogger(__name__)

settings_bp = Blueprint(
    "settings",
    __name__,
    url_prefix="/api/settings",
)


@settings_bp.get("")
def settings():
    _, error = require_role("staff")
    if error:
        return error
    try:
        settings_data = load_settings()
        return jsonify(
            {
                "success": True,
                "message": "Settings retrieved successfully.",
                "data": settings_data,
            }
        ), 200
    except Exception:
        logger.exception("Failed to load settings.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@settings_bp.post("")
def update_settings():
    _, error = require_role("staff")
    if error:
        return error
    try:
        payload = request.get_json(silent=True) or {}
        save_settings(payload)
        logger.info("Application settings updated.")
        return jsonify(
            {
                "success": True,
                "message": "Settings updated successfully.",
                "data": {"status": "saved"},
            }
        ), 200
    except Exception:
        logger.exception("Failed to update settings.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500