from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request

from ..request_validation import (
    require_login,
    require_role,
)

from ..db import (
    list_student_appointments,
    list_staff_appointments,
)

from ..services.appointment_service import (
    create_student_appointment,
    cancel_student_appointment,
    reschedule_student_appointment,
    create_manual_appointment,
    update_appointment_status_service,
    update_counselor_notes_service,
    get_appointment_details_service,
)


appointment_bp = Blueprint(
    "appointments",
    __name__,
    url_prefix="/api/appointments",
)

logger = logging.getLogger(__name__)


@appointment_bp.get("")
def list_staff_appointments_route():
    user, error = require_role("staff")
    if error:
        return error

    items = list_staff_appointments(user["id"])

    return jsonify({"items": items}), 200


@appointment_bp.post("")
def create_appointment():
    payload = request.get_json(silent=True) or {}
    user = require_login()

    if not user:
        return jsonify({"error": "Login required."}), 401

    try:
        appointment_id = create_student_appointment(user, payload)
    except ValueError as exc:
        message, fields = exc.args[0]
        return jsonify({"error": message, "fields": fields}), 400
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 409
    except LookupError as exc:
        message = str(exc)
        status = 404 if "Student account" in message else 400
        return jsonify({"error": message}), status

    logger.info("Student %s created appointment %s", user["id"], appointment_id)
    return jsonify({"id": appointment_id, "status": "saved"}), 201


@appointment_bp.get("/my")
def my_appointments():
    user, error = require_role("student")
    if error:
        return error

    return jsonify(
        {
            "items": list_student_appointments(
                user["id"]
            )
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
        return jsonify({"error": str(exc)}), 404
    except PermissionError as exc:
        return jsonify({"error": str(exc)}), 403
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 400
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    logger.info("Student %s cancelled appointment %s", user["id"], appointment_id)
    return jsonify({"status": "cancelled"}), 200


@appointment_bp.post("/my/<int:appointment_id>/reschedule")
def reschedule_my_appointment(appointment_id: int):
    user, error = require_role("student")
    if error:
        return error

    payload = request.get_json(silent=True) or {}

    try:
        new_id = reschedule_student_appointment(user, appointment_id, payload)
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except PermissionError as exc:
        return jsonify({"error": str(exc)}), 403
    except RuntimeError as exc:
        status = 409 if str(exc) == "This schedule is already taken." else 400
        return jsonify({"error": str(exc)}), status
    except ValueError as exc:
        if exc.args and isinstance(exc.args[0], tuple):
            message, fields = exc.args[0]
            return jsonify({"error": message, "fields": fields}), 400
        return jsonify({"error": str(exc)}), 400

    logger.info(
        "Student %s rescheduled appointment %s -> %s",
        user["id"],
        appointment_id,
        new_id,
    )
    return jsonify({"status": "rescheduled", "appointment_id": new_id}), 201


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
            return jsonify({"error": message, "fields": fields}), 400
        return jsonify({"error": str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 409
    except LookupError as exc:
        message = str(exc)
        status = 404 if "Student account" in message else 400
        return jsonify({"error": message}), status

    logger.info("Staff %s created manual appointment %s", user["id"], appointment_id)
    return jsonify({"id": appointment_id, "status": "created"}), 201


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
        return jsonify({"error": str(exc)}), 400
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 400

    logger.info(
        "Staff %s updated appointment %s to status '%s'",
        user["id"],
        appointment_id,
        status,
    )
    return jsonify({"status": "updated"}), 200


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
        return jsonify({"error": str(exc)}), 404

    return jsonify(appointment), 200


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
        return jsonify({"error": str(exc)}), 404
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 400
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    logger.info(
        "Staff %s updated counselor notes for appointment %s",
        user["id"],
        appointment_id,
    )
    return jsonify({"status": "saved"}), 200
