from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request

from ..request_validation import (
    require_any_role,
    require_login,
    require_role,
)

from ..services.appointment_service import (
    create_student_appointment,
    cancel_student_appointment,
    reschedule_student_appointment,
    create_manual_appointment,
    update_appointment_status_service,
    update_counselor_notes_service,
    get_appointment_details_service,
    list_staff_appointments_service,
    list_student_appointments_service,
)
from ..services.settings_service import settings_service


appointment_bp = Blueprint(
    "appointments",
    __name__,
    url_prefix="/api/appointments",
)

logger = logging.getLogger(__name__)


@appointment_bp.get("/booking-options")
def booking_options_route():
    _, error = require_any_role("student", "staff")
    if error:
        return error

    return jsonify(
        {
            "success": True,
            "message": "Appointment booking options retrieved successfully.",
            "data": settings_service.get_student_booking_options(),
        }
    ), 200


@appointment_bp.get("")
def list_staff_appointments_route():
    user, error = require_role("staff")
    if error:
        return error

    items = list_staff_appointments_service(user)

    return jsonify(
        {
            "success": True,
            "message": "Appointments retrieved successfully.",
            "data": {"items": items},
        }
    ), 200


@appointment_bp.post("")
def create_appointment():
    payload = request.get_json(silent=True) or {}
    user = require_login()

    if not user:
        return jsonify(
            {
                "success": False,
                "message": "Login required.",
                "errors": None,
            }
        ), 401

    try:
        appointment_id = create_student_appointment(user, payload)
    except ValueError as exc:
        message, fields = exc.args[0]
        return jsonify(
            {
                "success": False,
                "message": message,
                "errors": fields,
            }
        ), 400
    except RuntimeError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 409
    except LookupError as exc:
        message = str(exc)
        status = 404 if "Student account" in message else 400
        return jsonify(
            {
                "success": False,
                "message": message,
                "errors": None,
            }
        ), status

    logger.info("Student %s created appointment %s", user["id"], appointment_id)
    return jsonify(
        {
            "success": True,
            "message": "Appointment created successfully.",
            "data": {"id": appointment_id, "status": "saved"},
        }
    ), 201


@appointment_bp.get("/my")
def my_appointments():
    user, error = require_role("student")
    if error:
        return error

    items = list_student_appointments_service(user)
    return jsonify(
        {
            "success": True,
            "message": "Appointments retrieved successfully.",
            "data": {"items": items},
        }
    ), 200


@appointment_bp.patch("/my/<int:appointment_id>/cancel")
def cancel_my_appointment(appointment_id: int):
    user, error = require_role("student")
    if error:
        return error

    try:
        cancel_student_appointment(user, appointment_id)
    except LookupError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 404
    except PermissionError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 403
    except RuntimeError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400
    except ValueError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400

    logger.info("Student %s cancelled appointment %s", user["id"], appointment_id)
    return jsonify(
        {
            "success": True,
            "message": "Appointment cancelled successfully.",
            "data": {"status": "cancelled"},
        }
    ), 200


@appointment_bp.post("/my/<int:appointment_id>/reschedule")
def reschedule_my_appointment(appointment_id: int):
    user, error = require_role("student")
    if error:
        return error

    payload = request.get_json(silent=True) or {}

    try:
        new_id = reschedule_student_appointment(user, appointment_id, payload)
    except LookupError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 404
    except PermissionError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 403
    except RuntimeError as exc:
        status = 409 if str(exc) == "This schedule is already taken." else 400
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), status
    except ValueError as exc:
        if exc.args and isinstance(exc.args[0], tuple):
            message, fields = exc.args[0]
            return jsonify(
                {
                    "success": False,
                    "message": message,
                    "errors": fields,
                }
            ), 400
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400

    logger.info(
        "Student %s rescheduled appointment %s -> %s",
        user["id"],
        appointment_id,
        new_id,
    )
    return jsonify(
        {
            "success": True,
            "message": "Appointment rescheduled successfully.",
            "data": {"status": "rescheduled", "appointment_id": new_id},
        }
    ), 201


@appointment_bp.post("/manual")
def create_manual_appointment_route():
    user, error = require_role("staff")
    if error:
        return error

    payload = request.get_json(silent=True) or {}

    try:
        appointment_id = create_manual_appointment(user, payload)
    except ValueError as exc:
        if exc.args and isinstance(exc.args[0], tuple):
            message, fields = exc.args[0]
            return jsonify(
                {
                    "success": False,
                    "message": message,
                    "errors": fields,
                }
            ), 400
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400
    except RuntimeError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 409
    except LookupError as exc:
        message = str(exc)
        status = 404 if "Student account" in message else 400
        return jsonify(
            {
                "success": False,
                "message": message,
                "errors": None,
            }
        ), status

    logger.info("Staff %s created manual appointment %s", user["id"], appointment_id)
    return jsonify(
        {
            "success": True,
            "message": "Manual appointment created successfully.",
            "data": {"id": appointment_id, "status": "created"},
        }
    ), 201


@appointment_bp.patch("/<int:appointment_id>")
def change_appointment(appointment_id: int):
    payload = request.get_json(silent=True) or {}
    user, error = require_role("staff")
    if error:
        return error

    status = str(payload.get("status", "")).strip() or "pending"

    try:
        update_appointment_status_service(user, appointment_id, status)
    except ValueError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400
    except LookupError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 404
    except RuntimeError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400

    logger.info(
        "Staff %s updated appointment %s to status '%s'",
        user["id"],
        appointment_id,
        status,
    )
    return jsonify(
        {
            "success": True,
            "message": "Appointment status updated successfully.",
            "data": {"status": "updated"},
        }
    ), 200


@appointment_bp.get("/<int:appointment_id>")
def appointment_details(appointment_id: int):
    user, error = require_role("staff")
    if error:
        return error

    try:
        appointment = get_appointment_details_service(
            user,
            appointment_id,
        )
    except LookupError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 404

    return jsonify(
        {
            "success": True,
            "message": "Appointment details retrieved successfully.",
            "data": appointment,
        }
    ), 200


@appointment_bp.patch("/<int:appointment_id>/notes")
def update_counselor_notes_route(appointment_id: int):
    user, error = require_role("staff")
    if error:
        return error

    payload = request.get_json(silent=True) or {}
    notes = str(payload.get("counselor_notes", "")).strip()

    try:
        update_counselor_notes_service(user, appointment_id, notes)
    except LookupError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 404
    except RuntimeError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400
    except ValueError as exc:
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400

    logger.info(
        "Staff %s updated counselor notes for appointment %s",
        user["id"],
        appointment_id,
    )
    return jsonify(
        {
            "success": True,
            "message": "Counselor notes updated successfully.",
            "data": {"status": "saved"},
        }
    ), 200
