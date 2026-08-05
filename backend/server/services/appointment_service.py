from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import date, datetime, timedelta
from typing import Final

from ..db import (
    current_time,
    AppointmentConflictLockError,
    AppointmentConflictPersistenceError,
    fetch_rows,
    get_staff_by_program,
    get_student_by_id,
    list_appointments_by_date,
    load_settings,
    save_appointment_if_available,
    get_appointment_by_id,
    list_staff_appointments,
    list_student_appointments,
    save_notification,
    update_appointment_status,
    update_counselor_notes,
)


logger = logging.getLogger(__name__)

MODIFICATION_DEADLINE: Final[timedelta] = timedelta(hours=1)
CONFLICT_BLOCKING_STATUSES: Final[frozenset[str]] = frozenset(
    {"pending", "confirmed"}
)
CONFLICT_ERROR_MESSAGE: Final[str] = "This schedule is already taken."
CONSULTATION_SCHEDULE_FIELDS: Final[frozenset[str]] = frozenset(
    {"room", "days", "time"}
)
CONSULTATION_SCHEDULE_ERROR_MESSAGE: Final[str] = (
    "The selected date and time are outside the counselor's consultation schedule."
)
APPOINTMENT_AVAILABILITY_SETTING_KEY: Final[str] = "appointmentAvailability"
APPOINTMENT_AVAILABILITY_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "officeAvailability",
        "holidays",
        "academicCalendarExclusions",
        "unavailableDates",
    }
)
OFFICE_AVAILABILITY_FIELDS: Final[frozenset[str]] = frozenset(
    {"days", "time"}
)
APPOINTMENT_AVAILABILITY_ERROR_MESSAGE: Final[str] = (
    "The Guidance Office is unavailable for the selected date and time."
)
WEEKDAY_INDEXES: Final[dict[str, int]] = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

APPOINTMENT_STATES: Final[frozenset[str]] = frozenset(
    {
        "pending",
        "confirmed",
        "cancelled",
        "rejected",
        "completed",
    }
)
APPOINTMENT_STATUS_ORDER: Final[tuple[str, ...]] = (
    "pending",
    "confirmed",
    "cancelled",
    "rejected",
    "completed",
)
ALLOWED_STATUS_TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    "pending": frozenset({"confirmed", "rejected", "cancelled"}),
    "confirmed": frozenset({"completed", "cancelled"}),
    "cancelled": frozenset(),
    "rejected": frozenset(),
    "completed": frozenset(),
}
STAFF_NOTIFICATION_TEMPLATES: Final[dict[str, tuple[str, str]]] = {
    "appointment_request": (
        "New appointment request",
        "{student_name} requested an appointment on {preferred_date} at {preferred_time_slot}.",
    ),
    "appointment_cancelled": (
        "Appointment cancelled",
        "{student_name} cancelled an appointment on {preferred_date} at {preferred_time_slot}.",
    ),
    "appointment_rescheduled": (
        "Appointment rescheduled",
        "{student_name} rescheduled an appointment to {preferred_date} at {preferred_time_slot}.",
    ),
}
STUDENT_NOTIFICATION_TEMPLATES: Final[dict[str, tuple[str, str, str]]] = {
    "confirmed": (
        "appointment_confirmed",
        "Appointment confirmed",
        "Your appointment on {preferred_date} at {preferred_time_slot} has been confirmed.",
    ),
    "rejected": (
        "appointment_rejected",
        "Appointment rejected",
        "Your appointment on {preferred_date} at {preferred_time_slot} has been rejected.",
    ),
    "cancelled": (
        "appointment_cancelled",
        "Appointment cancelled",
        "Your appointment on {preferred_date} at {preferred_time_slot} has been cancelled.",
    ),
}

# Helper: students may only modify appointments at least 1 hour before scheduled time
def can_student_modify_appointment(appointment_record: dict) -> bool:
    appointment_datetime = datetime.strptime(
        f"{appointment_record['preferred_date']} {appointment_record['preferred_time_slot']}",
        "%Y-%m-%d %I:%M %p",
    )

    return (
        appointment_datetime - datetime.now()
        >= MODIFICATION_DEADLINE
    )


def _require_student_ownership(student_account: dict, appointment: dict) -> None:
    if appointment["account_id"] != student_account["id"]:
        raise PermissionError("You may only manage your own appointments.")


def _require_staff_assignment(staff_account: dict, appointment_id: int) -> None:
    allowed = {
        item["id"] for item in list_staff_appointments(staff_account["id"])
    }
    if appointment_id not in allowed:
        raise LookupError("Appointment not found.")


def list_student_appointments_service(
    student_account: dict,
) -> list[dict]:
    appointments = list_student_appointments(student_account["id"])

    return [
        {
            field: value
            for field, value in appointment.items()
            if field != "counselor_notes"
        }
        for appointment in appointments
    ]


def list_staff_appointments_service(
    staff_account: dict,
) -> list[dict]:
    return list_staff_appointments(staff_account["id"])


def _parse_analytics_filter_date(
    value: object,
    field_name: str,
) -> date | None:
    if value is None or not str(value).strip():
        return None

    try:
        return date.fromisoformat(str(value).strip())
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name}.") from exc


def _appointment_date_value(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def get_appointment_analytics_service(
    staff_account: dict,
    *,
    start_date: object = None,
    end_date: object = None,
) -> dict:
    """Return read-only analytics for the staff member's authorized programs."""
    start = _parse_analytics_filter_date(start_date, "start date")
    end = _parse_analytics_filter_date(end_date, "end date")

    if start and end and start > end:
        raise ValueError("Start date must not be after end date.")

    appointments = list_staff_appointments_service(staff_account)
    filtered_appointments: list[tuple[dict, date]] = []

    for appointment in appointments:
        appointment_date = _appointment_date_value(appointment["preferred_date"])
        if start and appointment_date < start:
            continue
        if end and appointment_date > end:
            continue
        filtered_appointments.append((appointment, appointment_date))

    status_counts = Counter(
        str(appointment.get("status", "")).lower()
        for appointment, _ in filtered_appointments
    )
    daily_counts: Counter[str] = Counter()
    weekly_counts: Counter[str] = Counter()
    monthly_counts: Counter[str] = Counter()
    program_counts: Counter[str] = Counter()
    counselor_counts: Counter[str] = Counter()
    counselor_by_program: dict[str, str | None] = {}

    for appointment, appointment_date in filtered_appointments:
        daily_counts[appointment_date.isoformat()] += 1
        iso_year, iso_week, _ = appointment_date.isocalendar()
        weekly_counts[f"{iso_year}-W{iso_week:02d}"] += 1
        monthly_counts[appointment_date.strftime("%Y-%m")] += 1

        program = str(appointment.get("program") or "").strip()
        if not program:
            continue

        program_counts[program] += 1
        if program not in counselor_by_program:
            counselor = get_staff_by_program(program)
            counselor_by_program[program] = (
                str(counselor.get("full_name") or "").strip()
                if counselor
                else None
            )

        counselor_name = counselor_by_program[program]
        if counselor_name:
            counselor_counts[counselor_name] += 1

    def count_rows(counter: Counter[str], key: str) -> list[dict]:
        return [
            {key: label, "count": count}
            for label, count in sorted(counter.items())
        ]

    return {
        "filters": {
            "start_date": start.isoformat() if start else None,
            "end_date": end.isoformat() if end else None,
        },
        "total_appointments": len(filtered_appointments),
        "status_distribution": [
            {"status": status, "count": status_counts[status]}
            for status in APPOINTMENT_STATUS_ORDER
        ],
        "daily_trends": count_rows(daily_counts, "date"),
        "weekly_trends": count_rows(weekly_counts, "week"),
        "monthly_trends": count_rows(monthly_counts, "month"),
        "counselor_counts": count_rows(counselor_counts, "counselor_name"),
        "program_statistics": count_rows(program_counts, "program"),
    }


def _normalize_preferred_time_slot(value: object) -> str:
    time_slot = str(value).strip()

    try:
        return datetime.strptime(time_slot, "%I:%M %p").strftime("%I:%M %p")
    except ValueError:
        # Preserve existing behavior for nonstandard values. Broader appointment
        # time validation belongs to the later validation-centralization milestone.
        return time_slot


# Appointments persist only a start time, so this intentionally compares
# normalized start-time equality rather than time intervals.
def _has_appointment_conflict(
    preferred_date: str,
    preferred_time_slot: str,
) -> bool:
    normalized_time_slot = _normalize_preferred_time_slot(preferred_time_slot)

    for appointment in list_appointments_by_date(preferred_date):
        status = str(appointment.get("status", "")).lower()
        if status not in CONFLICT_BLOCKING_STATUSES:
            continue

        existing_time_slot = _normalize_preferred_time_slot(
            appointment.get("preferred_time_slot", "")
        )
        if existing_time_slot == normalized_time_slot:
            return True

    return False


def _equivalent_stored_time_slots(value: object) -> tuple[str, ...]:
    """Return stored text forms equivalent under the existing normalization."""
    time_slot = str(value).strip()
    normalized_time_slot = _normalize_preferred_time_slot(time_slot)

    try:
        datetime.strptime(time_slot, "%I:%M %p")
    except ValueError:
        return (normalized_time_slot,)

    unpadded_hour = str(int(normalized_time_slot[:2]))
    unpadded_time_slot = f"{unpadded_hour}{normalized_time_slot[2:]}"
    return tuple(dict.fromkeys((normalized_time_slot, unpadded_time_slot)))


def _save_appointment_with_atomic_conflict_check(payload: dict) -> int:
    """Persist after service validation with a final database-owned recheck."""
    try:
        return save_appointment_if_available(
            payload,
            normalized_time_slot=_normalize_preferred_time_slot(
                payload["preferred_time_slot"]
            ),
            equivalent_time_slots=_equivalent_stored_time_slots(
                payload["preferred_time_slot"]
            ),
        )
    except (
        AppointmentConflictPersistenceError,
        AppointmentConflictLockError,
    ) as exc:
        raise RuntimeError(CONFLICT_ERROR_MESSAGE) from exc


def _decode_consultation_metadata_list(value: object) -> list[object] | None:
    if isinstance(value, bytes):
        try:
            value = value.decode("utf-8")
        except UnicodeDecodeError:
            return None

    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return None

    return value if isinstance(value, list) else None


def _parse_schedule_days(value: object) -> set[int] | None:
    if not isinstance(value, str):
        return None

    days = " ".join(value.strip().split())
    if not days:
        return None

    normalized_days = days.casefold()
    if " to " in normalized_days:
        separator_index = normalized_days.find(" to ")
        start_name = days[:separator_index].strip()
        end_name = days[separator_index + len(" to "):].strip()
    elif "-" in days:
        day_names = days.split("-")
        if len(day_names) != 2:
            return None
        start_name, end_name = (name.strip() for name in day_names)
    else:
        weekday = WEEKDAY_INDEXES.get(normalized_days)
        return {weekday} if weekday is not None else None

    start_day = WEEKDAY_INDEXES.get(start_name.casefold())
    end_day = WEEKDAY_INDEXES.get(end_name.casefold())
    if start_day is None or end_day is None or start_day > end_day:
        return None

    return set(range(start_day, end_day + 1))


def _parse_clock(value: object) -> int | None:
    if not isinstance(value, str):
        return None

    clock = " ".join(value.strip().split())
    clock_parts = clock.split(" ")
    if len(clock_parts) != 2:
        return None

    hour_and_minute, meridiem = clock_parts
    if meridiem.casefold() not in {"am", "pm"}:
        return None

    time_parts = hour_and_minute.split(":")
    if len(time_parts) != 2:
        return None

    hour_text, minute_text = time_parts
    if (
        not hour_text.isdigit()
        or not minute_text.isdigit()
        or not 1 <= len(hour_text) <= 2
        or len(minute_text) != 2
    ):
        return None

    hour = int(hour_text)
    minute = int(minute_text)
    if not 1 <= hour <= 12 or not 0 <= minute <= 59:
        return None

    if hour == 12:
        hour = 0
    if meridiem.casefold() == "pm":
        hour += 12

    return hour * 60 + minute


def _parse_schedule_time_range(value: object) -> tuple[int, int] | None:
    if not isinstance(value, str):
        return None

    time_range = " ".join(value.strip().split())
    clocks = time_range.split("-")
    if len(clocks) != 2:
        return None

    start_time = _parse_clock(clocks[0])
    end_time = _parse_clock(clocks[1])
    if start_time is None or end_time is None or start_time >= end_time:
        return None

    return start_time, end_time


def _has_valid_consultation_schedule(
    counselor: dict,
    preferred_date: object,
    preferred_time_slot: object,
) -> bool:
    if not isinstance(preferred_date, str):
        return False

    date_text = preferred_date.strip()
    if (
        len(date_text) != 10
        or date_text[4] != "-"
        or date_text[7] != "-"
        or not date_text[:4].isdigit()
        or not date_text[5:7].isdigit()
        or not date_text[8:].isdigit()
    ):
        return False

    try:
        requested_weekday = datetime.strptime(date_text, "%Y-%m-%d").weekday()
    except ValueError:
        return False

    requested_time = _parse_clock(
        _normalize_preferred_time_slot(preferred_time_slot)
    )
    if requested_time is None:
        return False

    raw_rooms = _decode_consultation_metadata_list(
        counselor.get("consultation_rooms")
    )
    raw_schedules = _decode_consultation_metadata_list(
        counselor.get("consultation_schedules")
    )
    if not raw_rooms or not raw_schedules:
        return False

    rooms: set[str] = set()
    for raw_room in raw_rooms:
        if not isinstance(raw_room, str):
            return False
        room = raw_room.strip()
        if not room or room in rooms:
            return False
        rooms.add(room)

    has_matching_schedule = False
    for schedule in raw_schedules:
        if (
            not isinstance(schedule, dict)
            or set(schedule) != CONSULTATION_SCHEDULE_FIELDS
        ):
            return False

        room = schedule.get("room")
        if not isinstance(room, str) or room.strip() not in rooms:
            return False

        scheduled_days = _parse_schedule_days(schedule.get("days"))
        time_range = _parse_schedule_time_range(schedule.get("time"))
        if scheduled_days is None or time_range is None:
            return False

        start_time, end_time = time_range
        if (
            requested_weekday in scheduled_days
            and start_time <= requested_time < end_time
        ):
            has_matching_schedule = True

    return has_matching_schedule


def _validate_consultation_schedule(
    counselor: dict,
    preferred_date: object,
    preferred_time_slot: object,
) -> None:
    if not _has_valid_consultation_schedule(
        counselor,
        preferred_date,
        preferred_time_slot,
    ):
        raise ValueError(
            (
                CONSULTATION_SCHEDULE_ERROR_MESSAGE,
                ["preferred_date", "preferred_time_slot"],
            )
        )


def _load_appointment_availability() -> dict | None:
    availability = load_settings().get(APPOINTMENT_AVAILABILITY_SETTING_KEY)

    if isinstance(availability, bytes):
        try:
            availability = availability.decode("utf-8")
        except UnicodeDecodeError:
            return None

    if isinstance(availability, str):
        try:
            availability = json.loads(availability)
        except json.JSONDecodeError:
            return None

    return availability if isinstance(availability, dict) else None


def _parse_availability_date(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None

    date_text = value.strip()
    if (
        len(date_text) != 10
        or date_text[4] != "-"
        or date_text[7] != "-"
        or not date_text[:4].isdigit()
        or not date_text[5:7].isdigit()
        or not date_text[8:].isdigit()
    ):
        return None

    try:
        return datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        return None


def _parse_unavailable_dates(value: object) -> set[str] | None:
    if not isinstance(value, list):
        return None

    dates: set[str] = set()
    for raw_date in value:
        if not isinstance(raw_date, str) or raw_date != raw_date.strip():
            return None

        parsed_date = _parse_availability_date(raw_date)
        if parsed_date is None:
            return None

        date_text = parsed_date.strftime("%Y-%m-%d")
        if date_text in dates:
            return None
        dates.add(date_text)

    return dates


def _has_valid_appointment_availability(
    preferred_date: object,
    preferred_time_slot: object,
) -> bool:
    availability = _load_appointment_availability()
    if (
        availability is None
        or set(availability) != APPOINTMENT_AVAILABILITY_FIELDS
    ):
        return False

    requested_date = _parse_availability_date(preferred_date)
    requested_time = _parse_clock(
        _normalize_preferred_time_slot(preferred_time_slot)
    )
    if requested_date is None or requested_time is None:
        return False

    office_availability = availability.get("officeAvailability")
    if not isinstance(office_availability, list) or not office_availability:
        return False

    closed_dates: set[str] = set()
    for field in (
        "holidays",
        "academicCalendarExclusions",
        "unavailableDates",
    ):
        unavailable_dates = _parse_unavailable_dates(availability.get(field))
        if unavailable_dates is None:
            return False
        closed_dates.update(unavailable_dates)

    if requested_date.strftime("%Y-%m-%d") in closed_dates:
        return False

    has_matching_window = False
    for window in office_availability:
        if (
            not isinstance(window, dict)
            or set(window) != OFFICE_AVAILABILITY_FIELDS
        ):
            return False

        available_days = _parse_schedule_days(window.get("days"))
        time_range = _parse_schedule_time_range(window.get("time"))
        if available_days is None or time_range is None:
            return False

        start_time, end_time = time_range
        if (
            requested_date.weekday() in available_days
            and start_time <= requested_time < end_time
        ):
            has_matching_window = True

    return has_matching_window


def _validate_appointment_availability(
    preferred_date: object,
    preferred_time_slot: object,
) -> None:
    if not _has_valid_appointment_availability(
        preferred_date,
        preferred_time_slot,
    ):
        raise ValueError(
            (
                APPOINTMENT_AVAILABILITY_ERROR_MESSAGE,
                ["preferred_date", "preferred_time_slot"],
            )
        )


def _validate_required_fields(
    payload: dict,
    required_fields: list[str],
) -> None:
    missing_fields = [
        field
        for field in required_fields
        if not str(payload.get(field, "")).strip()
    ]

    if missing_fields:
        raise ValueError(("Missing required fields.", missing_fields))


def _resolve_student_and_counselor(
    student_id: int,
    counselor_not_found_message: str,
) -> tuple[dict, dict]:
    student = get_student_by_id(student_id)

    if not student:
        raise LookupError("Student account not found.")

    counselor = get_staff_by_program(
        str(student.get("program", "")).strip()
    )

    if counselor is None:
        raise LookupError(counselor_not_found_message)

    return student, counselor


def _validate_booking_constraints(
    counselor: dict,
    preferred_date: object,
    preferred_time_slot: object,
) -> None:
    _validate_consultation_schedule(
        counselor,
        preferred_date,
        preferred_time_slot,
    )
    _validate_appointment_availability(
        preferred_date,
        preferred_time_slot,
    )


def _save_appointment_notification_safely(
    recipient_account_id: int,
    title: str,
    message: str,
    notification_type: str,
) -> None:
    try:
        save_notification(
            {
                "recipient_account_id": recipient_account_id,
                "title": title,
                "message": message,
                "type": notification_type,
                "created_at": current_time(),
            }
        )
    except Exception:
        logger.exception(
            "Failed to persist appointment notification type '%s'.",
            notification_type,
        )


def _notify_routed_staff(
    counselor: dict,
    student: dict,
    preferred_date: object,
    preferred_time_slot: object,
    notification_type: str,
) -> None:
    try:
        title, message_template = STAFF_NOTIFICATION_TEMPLATES[notification_type]
        _save_appointment_notification_safely(
            int(counselor["id"]),
            title,
            message_template.format(
                student_name=student["full_name"],
                preferred_date=preferred_date,
                preferred_time_slot=preferred_time_slot,
            ),
            notification_type,
        )
    except Exception:
        logger.exception(
            "Failed to prepare appointment notification type '%s'.",
            notification_type,
        )


def _notify_currently_routed_staff(
    student_account_id: int,
    preferred_date: object,
    preferred_time_slot: object,
    notification_type: str,
) -> None:
    try:
        student, counselor = _resolve_student_and_counselor(
            student_account_id,
            "No counselor is currently assigned to the student's program.",
        )
        _notify_routed_staff(
            counselor,
            student,
            preferred_date,
            preferred_time_slot,
            notification_type,
        )
    except Exception:
        logger.exception(
            "Failed to resolve recipient for appointment notification type '%s'.",
            notification_type,
        )


def _notify_student_of_status_change(
    appointment: dict,
    status: str,
) -> None:
    notification = STUDENT_NOTIFICATION_TEMPLATES.get(status)
    if notification is None:
        return

    try:
        notification_type, title, message_template = notification
        _save_appointment_notification_safely(
            int(appointment["account_id"]),
            title,
            message_template.format(
                preferred_date=appointment["preferred_date"],
                preferred_time_slot=appointment["preferred_time_slot"],
            ),
            notification_type,
        )
    except Exception:
        logger.exception(
            "Failed to prepare appointment notification for status '%s'.",
            status,
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

    _validate_required_fields(payload, required_fields)

    if _has_appointment_conflict(
        payload["preferred_date"],
        payload["preferred_time_slot"],
    ):
        raise RuntimeError(CONFLICT_ERROR_MESSAGE)

    student, counselor = _resolve_student_and_counselor(
        student_account["id"],
        "No counselor is currently assigned to your program. "
        "Please contact the Guidance Office.",
    )

    _validate_booking_constraints(
        counselor,
        payload["preferred_date"],
        payload["preferred_time_slot"],
    )

    appointment_id = _save_appointment_with_atomic_conflict_check(
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
    _notify_routed_staff(
        counselor,
        student,
        payload["preferred_date"],
        payload["preferred_time_slot"],
        "appointment_request",
    )
    return appointment_id


def cancel_student_appointment(student_account: dict, appointment_id: int) -> None:
    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        raise LookupError("Appointment not found.")

    _require_student_ownership(student_account, appointment)

    if not can_student_modify_appointment(appointment):
        raise RuntimeError(
            "This appointment can no longer be modified because it is scheduled within the next hour."
        )

    if appointment["status"] != "pending":
        raise ValueError("Only pending appointments may be cancelled.")

    update_appointment_status(appointment_id, "cancelled")
    _notify_currently_routed_staff(
        student_account["id"],
        appointment["preferred_date"],
        appointment["preferred_time_slot"],
        "appointment_cancelled",
    )


def reschedule_student_appointment(
    student_account: dict,
    appointment_id: int,
    payload: dict,
) -> int:
    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        raise LookupError("Appointment not found.")

    _require_student_ownership(student_account, appointment)

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

    _validate_required_fields(payload, required_fields)

    if _has_appointment_conflict(
        payload["preferred_date"],
        payload["preferred_time_slot"],
    ):
        raise RuntimeError(CONFLICT_ERROR_MESSAGE)

    student, counselor = _resolve_student_and_counselor(
        student_account["id"],
        "No counselor is currently assigned to your program. "
        "Please contact the Guidance Office.",
    )

    _validate_booking_constraints(
        counselor,
        payload["preferred_date"],
        payload["preferred_time_slot"],
    )

    new_id = _save_appointment_with_atomic_conflict_check(
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
    _notify_routed_staff(
        counselor,
        student,
        payload["preferred_date"],
        payload["preferred_time_slot"],
        "appointment_rescheduled",
    )
    return new_id


def create_manual_appointment(staff_account: dict, payload: dict) -> int:
    required_fields = [
        "account_id",
        "appointment_category",
        "appointment_mode",
        "preferred_date",
        "preferred_time_slot",
        "reason",
        "appointment_source",
    ]

    _validate_required_fields(payload, required_fields)

    if payload["appointment_source"] not in {
        "walk_in",
        "hotline",
        "messenger",
        "email",
        "staff_manual",
    }:
        raise ValueError("Invalid appointment source.")

    student, counselor = _resolve_student_and_counselor(
        payload["account_id"],
        "No counselor is currently assigned to the student's program.",
    )

    if _has_appointment_conflict(
        payload["preferred_date"],
        payload["preferred_time_slot"],
    ):
        raise RuntimeError(CONFLICT_ERROR_MESSAGE)

    _validate_booking_constraints(
        counselor,
        payload["preferred_date"],
        payload["preferred_time_slot"],
    )

    return _save_appointment_with_atomic_conflict_check(
        {
            "account_id": payload["account_id"],
            "contact_number": student.get("contact_number") or "",
            "appointment_category": payload["appointment_category"],
            "appointment_mode": payload["appointment_mode"],
            "preferred_date": payload["preferred_date"],
            "preferred_time_slot": payload["preferred_time_slot"],
            "reason": payload["reason"],
            "status": "confirmed",
            "counselor_notes": None,
            "appointment_source": payload["appointment_source"],
            "created_at": current_time(),
            "updated_at": current_time(),
        }
    )


def update_appointment_status_service(
    staff_account: dict,
    appointment_id: int,
    status: str,
) -> None:
    if status not in APPOINTMENT_STATES:
        raise ValueError("Invalid appointment status.")

    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        raise LookupError("Appointment not found.")

    _require_staff_assignment(staff_account, appointment_id)

    current_status = appointment["status"]

    if status not in ALLOWED_STATUS_TRANSITIONS.get(current_status, frozenset()):
        raise RuntimeError(
            f"Cannot change appointment status from '{current_status}' to '{status}'."
        )

    if status == "completed" and not str(
        appointment.get("counselor_notes") or ""
    ).strip():
        raise ValueError(
            "Counselor notes are required for completed appointments."
        )

    update_appointment_status(appointment_id, status)
    _notify_student_of_status_change(appointment, status)


def update_counselor_notes_service(
    staff_account: dict,
    appointment_id: int,
    counselor_notes: str,
) -> None:
    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        raise LookupError("Appointment not found.")

    _require_staff_assignment(staff_account, appointment_id)

    counselor_notes = counselor_notes.strip()

    status = str(appointment.get("status", "")).lower()

    if status == "pending":
        raise RuntimeError(
            "Counselor notes cannot be added while the appointment is pending."
        )

    if status == "completed" and not counselor_notes:
        raise ValueError(
            "Counselor notes are required for completed appointments."
        )

    update_counselor_notes(appointment_id, counselor_notes)


def get_appointment_details_service(
    user: dict,
    appointment_id: int,
) -> dict:
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
            raise LookupError("Appointment not found.")

    if not rows:
        raise LookupError("Appointment not found.")

    if str(user.get("role", "")).lower() == "student":
        _require_student_ownership(user, rows[0])

    return rows[0]
