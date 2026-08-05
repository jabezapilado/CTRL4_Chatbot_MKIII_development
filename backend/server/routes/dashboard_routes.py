import logging
from flask import Blueprint, jsonify, request

from ..request_validation import require_role
from ..db import get_dashboard_stats
from ..services.appointment_service import get_appointment_analytics_service
from ..services.conversation_service import (
    get_chatbot_analytics_service,
    get_flagged_case_analytics_service,
)
from ..services.counselor_workload_service import (
    get_counselor_workload_analytics_service,
)

logger = logging.getLogger(__name__)


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard",
)


@dashboard_bp.get("/appointments/analytics")
def appointment_analytics():
    user, error = require_role("staff")
    if error:
        return error

    try:
        analytics = get_appointment_analytics_service(
            user,
            start_date=request.args.get("start_date"),
            end_date=request.args.get("end_date"),
        )
    except ValueError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400
    except Exception:
        logger.exception("Failed to retrieve appointment analytics.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    return jsonify(
        {
            "success": True,
            "message": "Appointment analytics retrieved successfully.",
            "data": analytics,
        }
    ), 200


@dashboard_bp.get("/chatbot/analytics")
def chatbot_analytics():
    _, error = require_role("staff")
    if error:
        return error

    try:
        analytics = get_chatbot_analytics_service(
            start_date=request.args.get("start_date"),
            end_date=request.args.get("end_date"),
        )
    except ValueError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400
    except Exception:
        logger.exception("Failed to retrieve chatbot analytics.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    return jsonify(
        {
            "success": True,
            "message": "Chatbot analytics retrieved successfully.",
            "data": analytics,
        }
    ), 200


@dashboard_bp.get("/counselor-workload")
def counselor_workload():
    user, error = require_role("staff")
    if error:
        return error

    try:
        analytics = get_counselor_workload_analytics_service(
            user,
            start_date=request.args.get("start_date"),
            end_date=request.args.get("end_date"),
        )
    except ValueError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400
    except Exception:
        logger.exception("Failed to retrieve counselor workload analytics.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    return jsonify(
        {
            "success": True,
            "message": "Counselor workload analytics retrieved successfully.",
            "data": analytics,
        }
    ), 200


@dashboard_bp.get("/flagged-cases/analytics")
def flagged_case_analytics():
    _, error = require_role("staff")
    if error:
        return error

    try:
        analytics = get_flagged_case_analytics_service(
            start_date=request.args.get("start_date"),
            end_date=request.args.get("end_date"),
        )
    except ValueError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400
    except Exception:
        logger.exception("Failed to retrieve flagged case analytics.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    return jsonify(
        {
            "success": True,
            "message": "Flagged case analytics retrieved successfully.",
            "data": analytics,
        }
    ), 200


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
