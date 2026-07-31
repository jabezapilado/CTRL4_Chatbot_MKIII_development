from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..auth import get_logged_in_user

from ..db import (
    fetch_rows,
    list_staff_appointments,
    list_student_appointments,
    get_appointment_by_id,
    update_appointment_status,
)

from ..services.appointment_service import (
    create_student_appointment,
    cancel_student_appointment,
    reschedule_student_appointment,
    create_manual_appointment,
    update_appointment_status_service,
    update_counselor_notes_service,
)

appointment_bp = Blueprint(
    "appointments",
    __name__,
    url_prefix="/api/appointments",
)


@appointment_bp.get("")
def list_staff_appointments_route():
    user = get_logged_in_user()

    if not user:
        return jsonify({"error": "Login required."}), 401

    role = str(user.get("role", "")).lower()

    if role != "staff":
        return jsonify(
            {
                "error": "Staff access required."
            }
        ), 403

    items = list_staff_appointments(user["id"])

    return jsonify({"items": items}), 200



@appointment_bp.post("")
def create_appointment():
    payload = request.get_json(silent=True) or {}
    user = get_logged_in_user()

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

    return jsonify({"id": appointment_id, "status": "saved"}), 201


@appointment_bp.get("/my")
def my_appointments():
    user = get_logged_in_user()

    if not user:
        return jsonify({"error": "Login required."}), 401
    if str(user.get("role", "student")).lower() != "student":
        return jsonify({"error": "Student access required."}), 403

    return jsonify(
        {
            "items": list_student_appointments(
                user["id"]
            )
        }
    ), 200



@appointment_bp.patch("/my/<int:appointment_id>/cancel")
def cancel_my_appointment(appointment_id: int):
    user = get_logged_in_user()

    if not user:
        return jsonify({"error": "Login required."}), 401
    if str(user.get("role", "student")).lower() != "student":
        return jsonify({"error": "Student access required."}), 403

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

    return jsonify({"status": "cancelled"}), 200


@appointment_bp.post("/my/<int:appointment_id>/reschedule")
def reschedule_my_appointment(appointment_id: int):
    user = get_logged_in_user()

    if not user:
        return jsonify({"error": "Login required."}), 401
    if str(user.get("role", "student")).lower() != "student":
        return jsonify({"error": "Student access required."}), 403

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

    return jsonify({"status": "rescheduled", "appointment_id": new_id}), 201



@appointment_bp.post("/manual")
def create_manual_appointment_route():
    user = get_logged_in_user()

    if not user or str(user.get("role", "")).lower() != "staff":
        return jsonify({"error": "Staff access required."}), 403

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

    return jsonify({"id": appointment_id, "status": "created"}), 201



@appointment_bp.patch("/<int:appointment_id>")
def change_appointment(appointment_id: int):
    payload = request.get_json(silent=True) or {}
    user = get_logged_in_user()

    if not user or str(user.get("role", "")).lower() != "staff":
        return jsonify({"error": "Staff access required."}), 403

    status = str(payload.get("status", "")).strip() or "pending"

    try:
        update_appointment_status_service(user, appointment_id, status)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"status": "updated"}), 200



@appointment_bp.get("/<int:appointment_id>")
def appointment_details(appointment_id: int):
    user = get_logged_in_user()

    if not user or str(user.get("role", "")).lower() != "staff":
        return jsonify({"error": "Staff access required."}), 403

    rows = fetch_rows(
        """
        SELECT
            appointments.*,
            accounts.full_name AS student_name,
            accounts.email AS student_email,
            accounts.student_number,
            accounts.program
        FROM appointments
        JOIN accounts
            ON appointments.account_id = accounts.id
        WHERE appointments.id = %s
        LIMIT 1
        """,
        (appointment_id,),
    )

    if str(user.get("role", "")).lower() == "staff":
        allowed = {
            appointment["id"]
            for appointment in list_staff_appointments(user["id"])
        }

        if appointment_id not in allowed:
            return jsonify({"error": "Appointment not found."}), 404

    if not rows:
        return jsonify({"error": "Appointment not found."}), 404

    return jsonify(rows[0]), 200



@appointment_bp.patch("/<int:appointment_id>/notes")
def update_counselor_notes_route(appointment_id: int):
    user = get_logged_in_user()

    if not user or str(user.get("role", "")).lower() != "staff":
        return jsonify({"error": "Staff access required."}), 403

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

    return jsonify({"status": "saved"}), 200
