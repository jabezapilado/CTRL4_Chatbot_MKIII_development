from __future__ import annotations

from typing import Final

from ..db import (
    create_case_note,
    fetch_case_note,
    fetch_flagged_conversation,
    list_case_notes,
    update_case_note,
)


MAX_CASE_NOTE_LENGTH: Final[int] = 5000
_NOTE_FIELDS: Final[tuple[str, ...]] = (
    "id",
    "note_text",
    "created_at",
    "updated_at",
)


def _project_note(note: dict) -> dict:
    return {field: note.get(field) for field in _NOTE_FIELDS}


def _require_flagged_case(conversation_summary_id: int) -> None:
    if fetch_flagged_conversation(conversation_summary_id) is None:
        raise LookupError("Flagged conversation not found.")


def _validate_note(note_text: str) -> str:
    normalized_note = str(note_text or "").strip()
    if not normalized_note:
        raise ValueError("Counselor note is required.")
    if len(normalized_note) > MAX_CASE_NOTE_LENGTH:
        raise ValueError("Counselor note must not exceed 5000 characters.")
    return normalized_note


def list_staff_case_notes(conversation_summary_id: int) -> list[dict]:
    """Return staff-permitted notes for an existing flagged conversation."""
    _require_flagged_case(conversation_summary_id)
    return [_project_note(note) for note in list_case_notes(conversation_summary_id)]


def create_staff_case_note(
    staff_account: dict,
    conversation_summary_id: int,
    note_text: str,
) -> dict:
    """Create a confidential staff note for an existing flagged conversation."""
    _require_flagged_case(conversation_summary_id)
    normalized_note = _validate_note(note_text)
    note_id = create_case_note(
        {
            "conversation_summary_id": conversation_summary_id,
            "staff_account_id": staff_account["id"],
            "note_text": normalized_note,
        }
    )
    note = fetch_case_note(note_id, conversation_summary_id)
    if note is None:
        raise RuntimeError("Counselor note could not be retrieved.")
    return _project_note(note)


def update_staff_case_note(
    staff_account: dict,
    conversation_summary_id: int,
    note_id: int,
    note_text: str,
) -> dict:
    """Edit a confidential note without moving it to another case."""
    del staff_account
    _require_flagged_case(conversation_summary_id)
    normalized_note = _validate_note(note_text)
    if not update_case_note(note_id, conversation_summary_id, normalized_note):
        raise LookupError("Counselor note not found.")
    note = fetch_case_note(note_id, conversation_summary_id)
    if note is None:
        raise RuntimeError("Counselor note could not be retrieved.")
    return _project_note(note)