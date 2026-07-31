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
        return jsonify(get_service_status()), 200
    except Exception:
        logger.exception("Health check failed.")
        return jsonify({"error": "Internal server error."}), 500