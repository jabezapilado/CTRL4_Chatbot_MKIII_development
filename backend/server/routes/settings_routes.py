import logging
from flask import Blueprint, jsonify, request

from ..request_validation import require_role
from ..services.settings_service import settings_service

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
        settings_data = settings_service.get_settings()
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
        settings_service.update_settings(payload)
        logger.info("Application settings updated.")
        return jsonify(
            {
                "success": True,
                "message": "Settings updated successfully.",
                "data": {"status": "saved"},
            }
        ), 200
    except ValueError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400
    except Exception:
        logger.exception("Failed to update settings.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@settings_bp.get("/faqs")
def list_faqs():
    _, error = require_role("staff")
    if error:
        return error
    try:
        return jsonify(
            {
                "success": True,
                "message": "FAQs retrieved successfully.",
                "data": {"items": settings_service.list_faqs()},
            }
        ), 200
    except Exception:
        logger.exception("Failed to load FAQs.")
        return jsonify(
            {"success": False, "message": "Internal server error.", "errors": None}
        ), 500


@settings_bp.post("/faqs")
def create_faq():
    _, error = require_role("staff")
    if error:
        return error
    try:
        entry = settings_service.create_faq(request.get_json(silent=True) or {})
        return jsonify(
            {"success": True, "message": "FAQ created successfully.", "data": entry}
        ), 201
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc), "errors": None}), 400
    except Exception:
        logger.exception("Failed to create FAQ.")
        return jsonify(
            {"success": False, "message": "Internal server error.", "errors": None}
        ), 500


@settings_bp.patch("/faqs/<string:faq_id>")
def update_faq(faq_id: str):
    _, error = require_role("staff")
    if error:
        return error
    try:
        entry = settings_service.update_faq(faq_id, request.get_json(silent=True) or {})
        return jsonify(
            {"success": True, "message": "FAQ updated successfully.", "data": entry}
        ), 200
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc), "errors": None}), 400
    except LookupError as exc:
        return jsonify({"success": False, "message": str(exc), "errors": None}), 404
    except Exception:
        logger.exception("Failed to update FAQ.")
        return jsonify(
            {"success": False, "message": "Internal server error.", "errors": None}
        ), 500


@settings_bp.delete("/faqs/<string:faq_id>")
def delete_faq(faq_id: str):
    _, error = require_role("staff")
    if error:
        return error
    try:
        settings_service.remove_faq(faq_id)
        return jsonify(
            {"success": True, "message": "FAQ removed successfully.", "data": None}
        ), 200
    except LookupError as exc:
        return jsonify({"success": False, "message": str(exc), "errors": None}), 404
    except Exception:
        logger.exception("Failed to remove FAQ.")
        return jsonify(
            {"success": False, "message": "Internal server error.", "errors": None}
        ), 500