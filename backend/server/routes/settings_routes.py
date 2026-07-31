import logging
from flask import Blueprint, jsonify, request

from ..db import load_settings, save_settings

logger = logging.getLogger(__name__)

settings_bp = Blueprint(
    "settings",
    __name__,
    url_prefix="/api/settings",
)


@settings_bp.get("")
def settings():
    try:
        return jsonify(load_settings()), 200
    except Exception:
        logger.exception("Failed to load settings.")
        return jsonify({"error": "Internal server error."}), 500


@settings_bp.post("")
def update_settings():
    try:
        payload = request.get_json(silent=True) or {}
        save_settings(payload)
        logger.info("Application settings updated.")
        return jsonify({"status": "saved"}), 200
    except Exception:
        logger.exception("Failed to update settings.")
        return jsonify({"error": "Internal server error."}), 500