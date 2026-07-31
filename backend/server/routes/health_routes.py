import logging
from flask import Blueprint, jsonify

from ..services import get_service_status

logger = logging.getLogger(__name__)

health_bp = Blueprint(
    "health",
    __name__,
)


@health_bp.get("/health")
def health():
    try:
        status = get_service_status()
        return jsonify(
            {
                "success": True,
                "message": "Service status retrieved successfully.",
                "data": status,
            }
        ), 200
    except Exception:
        logger.exception("Health check failed.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500