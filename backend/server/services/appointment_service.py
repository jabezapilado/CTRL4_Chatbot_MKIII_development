from __future__ import annotations

from datetime import datetime, timedelta

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