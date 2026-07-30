from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..auth import get_logged_in_user

from ..db import (
    current_time,
    fetch_rows,
    list_staff_appointments,
    list_student_appointments,
    save_appointment,
    has_appointment_conflict,
    get_appointment_by_id,
    update_appointment_status,
    get_staff_by_program,
    get_student_by_id,
    update_counselor_notes,
)

from ..services.appointment_service import (
    can_student_modify_appointment,
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

    required_fields = [
        "contact_number",
        "appointment_category",
        "appointment_mode",
        "preferred_date",
        "preferred_time_slot",
        "reason",
    ]
    missing_fields = [field for field in required_fields if not str(payload.get(field, "")).strip()]

    if missing_fields:
        return jsonify({"error": "Missing required fields.", "fields": missing_fields}), 400
    
    if has_appointment_conflict(
        payload["preferred_date"],
        payload["preferred_time_slot"],
    ):
        return jsonify(
            {
                "error": "This schedule is already taken."
            }
        ), 409

    student = get_student_by_id(user["id"])

    if not student:
        return jsonify({"error": "Student account not found."}), 404

    student_program = str(student.get("program", "")).strip()

    counselor = get_staff_by_program(student_program)

    if counselor is None:
        return jsonify(
            {
                "error": "No counselor is currently assigned to your program. Please contact the Guidance Office."
            }
        ), 400

    appointment_id = save_appointment(
        {
            "account_id": user["id"],
            "contact_number": payload["contact_number"],
            "appointment_category": payload["appointment_category"],
            "appointment_mode": payload["appointment_mode"],
            "preferred_date": payload["preferred_date"],
            "preferred_time_slot": payload["preferred_time_slot"],
            "reason": payload["reason"],
            "status": "pending",
            "counselor_notes": None,
            "appointment_source": "chatbot",
            "created_at": current_time(),
            "updated_at": current_time(),
        }
    )

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

    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        return jsonify({"error": "Appointment not found."}), 404

    if appointment["account_id"] != user["id"]:
        return jsonify({"error": "You may only cancel your own appointments."}), 403

    if not can_student_modify_appointment(appointment):
        return jsonify(
            {
                "error": "This appointment can no longer be modified because it is scheduled within the next hour."
            }
        ), 400

    if appointment["status"] != "pending":
        return jsonify(
            {"error": "Only pending appointments may be cancelled."}
        ), 400

    update_appointment_status(appointment_id, "cancelled")

    return jsonify({"status": "cancelled"}), 200


@appointment_bp.post("/my/<int:appointment_id>/reschedule")
def reschedule_my_appointment(appointment_id: int):
    user = get_logged_in_user()

    if not user:
        return jsonify({"error": "Login required."}), 401
    if str(user.get("role", "student")).lower() != "student":
        return jsonify({"error": "Student access required."}), 403

    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        return jsonify({"error": "Appointment not found."}), 404

    if appointment["account_id"] != user["id"]:
        return jsonify({"error": "You may only reschedule your own appointments."}), 403

    if appointment["status"] != "pending":
        return jsonify({"error": "Only pending appointments may be rescheduled."}), 400

    if not can_student_modify_appointment(appointment):
        return jsonify({
            "error": "This appointment can no longer be modified because it is scheduled within the next hour."
        }), 400

    payload = request.get_json(silent=True) or {}

    required_fields = [
        "preferred_date",
        "preferred_time_slot",
    ]

    missing = [field for field in required_fields if not str(payload.get(field, "")).strip()]
    if missing:
        return jsonify({"error": "Missing required fields.", "fields": missing}), 400

    if has_appointment_conflict(
        payload["preferred_date"],
        payload["preferred_time_slot"],
    ):
        return jsonify({"error": "This schedule is already taken."}), 409

    new_id = save_appointment(
        {
            "account_id": appointment["account_id"],
            "contact_number": appointment["contact_number"],
            "appointment_category": appointment["appointment_category"],
            "appointment_mode": appointment["appointment_mode"],
            "preferred_date": payload["preferred_date"],
            "preferred_time_slot": payload["preferred_time_slot"],
            "reason": appointment["reason"],
            "status": "pending",
            "counselor_notes": None,
            "appointment_source": appointment["appointment_source"],
            "created_at": current_time(),
            "updated_at": current_time(),
        }
    )
    update_appointment_status(appointment_id, "cancelled")

    return jsonify({"status": "rescheduled", "appointment_id": new_id}), 201




@appointment_bp.post("/manual")
def create_manual_appointment():
    user = get_logged_in_user()

    if not user or str(user.get("role", "")).lower() != "staff":
        return jsonify({"error": "Staff access required."}), 403

    payload = request.get_json(silent=True) or {}

    required_fields = [
        "account_id",
        "appointment_category",
        "appointment_mode",
        "preferred_date",
        "preferred_time_slot",
        "reason",
        "appointment_source",
    ]

    missing = [
        field
        for field in required_fields
        if not str(payload.get(field, "")).strip()
    ]

    if missing:
        return jsonify({"error": "Missing required fields.", "fields": missing}), 400

    if payload["appointment_source"] not in {
        "walk_in",
        "hotline",
        "messenger",
        "email",
        "staff_manual",
    }:
        return jsonify({"error": "Invalid appointment source."}), 400

    student = get_student_by_id(
        payload["account_id"]
    )

    if not student:
        return jsonify({"error": "Student account not found."}), 404

    counselor = get_staff_by_program(
        str(student["program"]).strip()
    )

    if counselor is None:
        return jsonify(
            {
                "error": (
                    "No counselor is currently assigned "
                    "to the student's program."
                )
            }
        ), 400

    if has_appointment_conflict(
        payload["preferred_date"],
        payload["preferred_time_slot"],
    ):
        return jsonify({"error": "This schedule is already taken."}), 409

    appointment_id = save_appointment(
        {
            "account_id": payload["account_id"],
            "contact_number": student.get("contact_number") or "",
            "appointment_category": payload["appointment_category"],
            "appointment_mode": payload["appointment_mode"],
            "preferred_date": payload["preferred_date"],
            "preferred_time_slot": payload["preferred_time_slot"],
            "reason": payload["reason"],
            "status": "approved",
            "counselor_notes": None,
            "appointment_source": payload["appointment_source"],
            "created_at": current_time(),
            "updated_at": current_time(),
        }
    )

    return jsonify({"id": appointment_id, "status": "created"}), 201



@appointment_bp.patch("/<int:appointment_id>")
def change_appointment(appointment_id: int):
    payload = request.get_json(silent=True) or {}
    user = get_logged_in_user()

    if not user or str(user.get("role", "")).lower() != "staff":
        return jsonify({"error": "Staff access required."}), 403

    status = str(payload.get("status", "")).strip() or "pending"
    VALID_STATUSES = {
        "pending",
        "approved",
        "done",
        "did_not_attend",
        "cancelled",
    }

    if status not in VALID_STATUSES:
        return jsonify(
            {
                "error": "Invalid appointment status."
            }
        ), 400

    appointment = get_appointment_by_id(
        appointment_id
    )

    if not appointment:
        return jsonify(
            {
                "error": "Appointment not found."
            }
        ), 404

    allowed = {
        item["id"]
        for item in list_staff_appointments(user["id"])
    }

    if appointment_id not in allowed:
        return jsonify({"error": "Appointment not found."}), 404

    current_status = appointment["status"]

    ALLOWED_TRANSITIONS = {
        "pending": {
            "approved",
            "cancelled",
        },
        "approved": {
            "done",
            "did_not_attend",
            "cancelled",
        },
        "done": set(),
        "did_not_attend": set(),
        "cancelled": set(),
    }

    if status not in ALLOWED_TRANSITIONS.get(
        current_status,
        set(),
    ):
        return jsonify(
            {
                "error":
                f"Cannot change appointment status from "
                f"'{current_status}' to '{status}'."
            }
        ), 400

    update_appointment_status(appointment_id, status,)
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

    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        return jsonify({"error": "Appointment not found."}), 404
    
    allowed = {
        item["id"]
        for item in list_staff_appointments(user["id"])
    }

    if appointment_id not in allowed:
        return jsonify(
            {
                "error": "Appointment not found."
            }
        ), 404

    payload = request.get_json(silent=True) or {}
    notes = str(payload.get("counselor_notes", "")).strip()
    
    status = str(appointment.get("status", "")).lower()

    if status == "pending":
        return jsonify(
            {
                "error": "Counselor notes cannot be added while the appointment is pending."
            }
        ), 400

    if status == "done" and not notes:
        return jsonify(
            {
                "error": "Counselor notes are required for completed appointments."
            }
        ), 400

    update_counselor_notes(
        appointment_id,
        notes,
    )

    return jsonify({"status": "saved"}), 200
