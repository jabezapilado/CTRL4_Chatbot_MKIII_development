from flask import Blueprint, jsonify

from ..services import get_service_status

health_bp = Blueprint(
    "health",
    __name__,
)


@health_bp.get("/health")
def health():
    return jsonify(get_service_status()), 200