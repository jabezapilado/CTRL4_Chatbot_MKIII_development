from flask import Blueprint, jsonify, request

from ..db import load_settings, save_settings

settings_bp = Blueprint(
    "settings",
    __name__,
    url_prefix="/api/settings",
)


@settings_bp.get("")
def settings():
    return jsonify(load_settings()), 200


@settings_bp.post("")
def update_settings():
    payload = request.get_json(silent=True) or {}
    save_settings(payload)
    return jsonify({"status": "saved"}), 200