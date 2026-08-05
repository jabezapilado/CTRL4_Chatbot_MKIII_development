from __future__ import annotations

from typing import Final

from ..db import (
    create_referral,
    create_referral_note,
    fetch_flagged_conversation,
    fetch_referral,
    list_referral_notes,
    list_referral_status_history,
    list_referrals,
    update_referral_status,
)


REFERRAL_DESTINATIONS: Final[frozenset[str]] = frozenset({
    "Guidance Counselor",
    "Psychologist",
    "Dean",
    "Student Affairs",
})
REFERRAL_STATUSES: Final[frozenset[str]] = frozenset({
    "pending",
    "in_progress",
    "completed",
    "cancelled",
})
INITIAL_REFERRAL_STATUS: Final[str] = "pending"
MAX_REFERRAL_REASON_LENGTH: Final[int] = 5000
MAX_REFERRAL_NOTE_LENGTH: Final[int] = 5000
_REFERRAL_FIELDS: Final[tuple[str, ...]] = (
    "id",
    "destination",
    "referral_reason",
    "status",
    "created_at",
    "updated_at",
)
_HISTORY_FIELDS: Final[tuple[str, ...]] = ("status", "created_at")
_NOTE_FIELDS: Final[tuple[str, ...]] = ("id", "note_text", "created_at")


def _project_fields(record: dict, fields: tuple[str, ...]) -> dict:
    return {field: record.get(field) for field in fields}


def _require_flagged_case(conversation_summary_id: int) -> None:
    if fetch_flagged_conversation(conversation_summary_id) is None:
        raise LookupError("Flagged conversation not found.")


def _validate_destination(destination: str) -> str:
    normalized_destination = str(destination or "").strip()
    if normalized_destination not in REFERRAL_DESTINATIONS:
        raise ValueError("Referral destination is not supported.")
    return normalized_destination


def _validate_required_text(value: str, label: str, maximum_length: int) -> str:
    normalized_value = str(value or "").strip()
    if not normalized_value:
        raise ValueError(f"Referral {label} is required.")
    if len(normalized_value) > maximum_length:
        raise ValueError(
            f"Referral {label} must not exceed {maximum_length} characters."
        )
    return normalized_value


def _validate_optional_note(note_text: str | None) -> str | None:
    if note_text is None:
        return None
    normalized_note = str(note_text).strip()
    if not normalized_note:
        return None
    if len(normalized_note) > MAX_REFERRAL_NOTE_LENGTH:
        raise ValueError(
            f"Referral note must not exceed {MAX_REFERRAL_NOTE_LENGTH} characters."
        )
    return normalized_note


def _validate_status(status: str) -> str:
    normalized_status = str(status or "").strip().lower()
    if normalized_status not in REFERRAL_STATUSES:
        raise ValueError("Referral status is not supported.")
    return normalized_status


def _project_referral(
    referral: dict,
    conversation_summary_id: int,
) -> dict:
    projected_referral = _project_fields(referral, _REFERRAL_FIELDS)
    referral_id = projected_referral["id"]
    projected_referral["status_history"] = [
        _project_fields(item, _HISTORY_FIELDS)
        for item in list_referral_status_history(referral_id, conversation_summary_id)
    ]
    projected_referral["notes"] = [
        _project_fields(item, _NOTE_FIELDS)
        for item in list_referral_notes(referral_id, conversation_summary_id)
    ]
    return projected_referral


def list_staff_referrals(conversation_summary_id: int) -> list[dict]:
    """Return staff-visible referrals and their append-only histories."""
    _require_flagged_case(conversation_summary_id)
    return [
        _project_referral(referral, conversation_summary_id)
        for referral in list_referrals(conversation_summary_id)
    ]


def create_staff_referral(
    staff_account: dict,
    conversation_summary_id: int,
    destination: str,
    referral_reason: str,
    note_text: str | None = None,
) -> dict:
    """Create an internal referral for an existing flagged conversation."""
    _require_flagged_case(conversation_summary_id)
    normalized_destination = _validate_destination(destination)
    normalized_reason = _validate_required_text(
        referral_reason,
        "reason",
        MAX_REFERRAL_REASON_LENGTH,
    )
    normalized_note = _validate_optional_note(note_text)
    referral_id = create_referral(
        {
            "conversation_summary_id": conversation_summary_id,
            "staff_account_id": staff_account["id"],
            "destination": normalized_destination,
            "referral_reason": normalized_reason,
            "status": INITIAL_REFERRAL_STATUS,
            "initial_note": normalized_note,
        }
    )
    referral = fetch_referral(referral_id, conversation_summary_id)
    if referral is None:
        raise RuntimeError("Referral could not be retrieved.")
    return _project_referral(referral, conversation_summary_id)


def update_staff_referral_status(
    staff_account: dict,
    conversation_summary_id: int,
    referral_id: int,
    status: str,
) -> dict:
    """Update a referral's current status while preserving its history."""
    _require_flagged_case(conversation_summary_id)
    normalized_status = _validate_status(status)
    referral = fetch_referral(referral_id, conversation_summary_id)
    if referral is None:
        raise LookupError("Referral not found.")
    if referral["status"] == normalized_status:
        raise ValueError("Referral already has that status.")
    if not update_referral_status(
        referral_id,
        conversation_summary_id,
        staff_account["id"],
        normalized_status,
    ):
        raise LookupError("Referral not found.")
    updated_referral = fetch_referral(referral_id, conversation_summary_id)
    if updated_referral is None:
        raise RuntimeError("Referral could not be retrieved.")
    return _project_referral(updated_referral, conversation_summary_id)


def add_staff_referral_note(
    staff_account: dict,
    conversation_summary_id: int,
    referral_id: int,
    note_text: str,
) -> dict:
    """Append an internal note to an existing referral."""
    _require_flagged_case(conversation_summary_id)
    if fetch_referral(referral_id, conversation_summary_id) is None:
        raise LookupError("Referral not found.")
    normalized_note = _validate_required_text(
        note_text,
        "note",
        MAX_REFERRAL_NOTE_LENGTH,
    )
    create_referral_note(
        {
            "referral_id": referral_id,
            "staff_account_id": staff_account["id"],
            "note_text": normalized_note,
        }
    )
    referral = fetch_referral(referral_id, conversation_summary_id)
    if referral is None:
        raise RuntimeError("Referral could not be retrieved.")
    return _project_referral(referral, conversation_summary_id)