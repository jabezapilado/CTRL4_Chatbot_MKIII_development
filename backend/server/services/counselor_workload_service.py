from __future__ import annotations

from collections import Counter
from datetime import date, datetime, time, timedelta

from ..db import (
    list_staff_appointments,
    list_staff_interventions_for_workload_analytics,
    list_staff_referrals_for_workload_analytics,
)


ACTIVE_REFERRAL_STATUSES = frozenset({"pending", "in_progress"})
ACTIVE_INTERVENTION_STATUSES = frozenset({"planned", "ongoing"})


def _parse_filter_date(value: object, field_name: str) -> date | None:
    if value is None or not str(value).strip():
        return None

    try:
        return date.fromisoformat(str(value).strip())
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name}.") from exc


def _date_range(
    start_date: object,
    end_date: object,
) -> tuple[date | None, date | None, datetime | None, datetime | None]:
    start = _parse_filter_date(start_date, "start date")
    end = _parse_filter_date(end_date, "end date")

    if start and end and start > end:
        raise ValueError("Start date must not be after end date.")

    return (
        start,
        end,
        datetime.combine(start, time.min) if start else None,
        datetime.combine(end + timedelta(days=1), time.min) if end else None,
    )


def _as_datetime(value: object) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def _within_range(
    record: dict,
    start_at: datetime | None,
    end_at: datetime | None,
) -> bool:
    created_at = _as_datetime(record["created_at"])
    return (
        (start_at is None or created_at >= start_at)
        and (end_at is None or created_at < end_at)
    )


def get_counselor_workload_analytics_service(
    staff_account: dict,
    *,
    start_date: object = None,
    end_date: object = None,
) -> dict:
    """Return aggregate workload data for one staff member's authorized scope."""
    start, end, start_at, end_at = _date_range(start_date, end_date)

    appointments = [
        appointment
        for appointment in list_staff_appointments(staff_account["id"])
        if _within_range(appointment, start_at, end_at)
    ]
    referrals = list_staff_referrals_for_workload_analytics(
        staff_account["id"],
        start_at,
        end_at,
    )
    interventions = list_staff_interventions_for_workload_analytics(
        staff_account["id"],
        start_at,
        end_at,
    )

    appointment_statuses = Counter(
        str(appointment.get("status") or "").strip().lower()
        for appointment in appointments
    )
    program_counts = Counter(
        str(appointment.get("program") or "").strip()
        for appointment in appointments
    )
    program_counts.pop("", None)

    return {
        "filters": {
            "start_date": start.isoformat() if start else None,
            "end_date": end.isoformat() if end else None,
        },
        "authorized_appointment_count": len(appointments),
        "pending_appointment_count": appointment_statuses["pending"],
        "confirmed_appointment_count": appointment_statuses["confirmed"],
        "completed_appointment_count": appointment_statuses["completed"],
        "active_referral_count": sum(
            str(referral.get("status") or "").strip().lower()
            in ACTIVE_REFERRAL_STATUSES
            for referral in referrals
        ),
        "active_intervention_count": sum(
            str(intervention.get("progress_status") or "").strip().lower()
            in ACTIVE_INTERVENTION_STATUSES
            for intervention in interventions
        ),
        "completed_intervention_count": sum(
            str(intervention.get("progress_status") or "").strip().lower()
            == "completed"
            for intervention in interventions
        ),
        "workload_by_program": [
            {"program": program, "count": count}
            for program, count in sorted(program_counts.items())
        ],
    }
