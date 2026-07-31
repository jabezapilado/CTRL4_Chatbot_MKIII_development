from __future__ import annotations

from datetime import datetime, timedelta

from ..db import (
    current_time,
    get_staff_by_program,
    get_student_by_id,
    has_appointment_conflict,
    save_appointment,
    get_appointment_by_id,
    update_appointment_status,
)

# Helper: students may only modify appointments at least 1 hour before scheduled time
def can_student_modify_appointment(appointment_record: dict) -> bool:
    appointment_datetime = datetime.strptime(
        f"{appointment_record['preferred_date']} {appointment_record['preferred_time_slot']}",
        "%Y-%m-%d %I:%M %p",
    )

    return (
        appointment_datetime - datetime.now()
        >= timedelta(hours=1)
    )


def create_student_appointment(student_account: dict, payload: dict) -> int:
    required_fields = [
        "contact_number",
        "appointment_category",
        "appointment_mode",
        "preferred_date",
        "preferred_time_slot",
        "reason",
    ]

    missing_fields = [
        field
        for field in required_fields
        if not str(payload.get(field, "")).strip()
    ]

    if missing_fields:
        raise ValueError(("Missing required fields.", missing_fields))

    if has_appointment_conflict(
        payload["preferred_date"],
        payload["preferred_time_slot"],
    ):
        raise RuntimeError("This schedule is already taken.")

    student = get_student_by_id(student_account["id"])

    if not student:
        raise LookupError("Student account not found.")

    counselor = get_staff_by_program(
        str(student.get("program", "")).strip()
    )

    if counselor is None:
        raise LookupError(
            "No counselor is currently assigned to your program. Please contact the Guidance Office."
        )

    return save_appointment(
        {
            "account_id": student_account["id"],
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


def cancel_student_appointment(student_account: dict, appointment_id: int) -> None:
    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        raise LookupError("Appointment not found.")

    if appointment["account_id"] != student_account["id"]:
        raise PermissionError("You may only cancel your own appointments.")

    if not can_student_modify_appointment(appointment):
        raise RuntimeError(
            "This appointment can no longer be modified because it is scheduled within the next hour."
        )

    if appointment["status"] != "pending":
        raise ValueError("Only pending appointments may be cancelled.")

    update_appointment_status(appointment_id, "cancelled")


def reschedule_student_appointment(
    student_account: dict,
    appointment_id: int,
    payload: dict,
) -> int:
    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        raise LookupError("Appointment not found.")

    if appointment["account_id"] != student_account["id"]:
        raise PermissionError("You may only reschedule your own appointments.")

    if appointment["status"] != "pending":
        raise ValueError("Only pending appointments may be rescheduled.")

    if not can_student_modify_appointment(appointment):
        raise RuntimeError(
            "This appointment can no longer be modified because it is scheduled within the next hour."
        )

    required_fields = [
        "preferred_date",
        "preferred_time_slot",
    ]

    missing_fields = [
        field
        for field in required_fields
        if not str(payload.get(field, "")).strip()
    ]

    if missing_fields:
        raise ValueError(("Missing required fields.", missing_fields))

    if has_appointment_conflict(
        payload["preferred_date"],
        payload["preferred_time_slot"],
    ):
        raise RuntimeError("This schedule is already taken.")

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
    return new_id
