from __future__ import annotations

from typing import Final

from ..db import (
    create_case_confidentiality,
    fetch_case_confidentiality,
    fetch_flagged_conversation,
    list_case_confidentiality_history,
    update_case_confidentiality,
)


CONFIDENTIAL: Final[str] = "confidential"
NOT_CONFIDENTIAL: Final[str] = "not_confidential"
CONFIDENTIALITY_STATUSES: Final[frozenset[str]] = frozenset({
    CONFIDENTIAL,
    NOT_CONFIDENTIAL,
})
MAX_CONFIDENTIALITY_REASON_LENGTH: Final[int] = 5000
_CONFIDENTIALITY_FIELDS: Final[tuple[str, ...]] = (
    "confidentiality_status",
    "confidentiality_reason",
    "created_at",
    "updated_at",
)
_HISTORY_FIELDS: Final[tuple[str, ...]] = (
    "confidentiality_status",
    "confidentiality_reason",
    "created_at",
)


def _project_fields(record: dict, fields: tuple[str, ...]) -> dict:
    return {field: record.get(field) for field in fields}


def _require_flagged_case(conversation_summary_id: int) -> None:
    if fetch_flagged_conversation(conversation_summary_id) is None:
        raise LookupError("Flagged conversation not found.")


def _validate_status(confidentiality_status: str) -> str:
    normalized_status = str(confidentiality_status or "").strip().lower()
    if normalized_status not in CONFIDENTIALITY_STATUSES:
        raise ValueError("Confidentiality status is not supported.")
    return normalized_status


def _validate_reason(
    confidentiality_status: str,
    confidentiality_reason: str | None,
) -> str | None:
    normalized_reason = str(confidentiality_reason or "").strip()
    if confidentiality_status == CONFIDENTIAL and not normalized_reason:
        raise ValueError("Confidentiality reason is required.")
    if len(normalized_reason) > MAX_CONFIDENTIALITY_REASON_LENGTH:
        raise ValueError(
            "Confidentiality reason must not exceed 5000 characters."
        )
    return normalized_reason or None


def _project_confidentiality(
    confidentiality: dict,
    conversation_summary_id: int,
) -> dict:
    projected_confidentiality = _project_fields(
        confidentiality,
        _CONFIDENTIALITY_FIELDS,
    )
    projected_confidentiality["history"] = [
        _project_fields(item, _HISTORY_FIELDS)
        for item in list_case_confidentiality_history(conversation_summary_id)
    ]
    return projected_confidentiality


def get_staff_case_confidentiality(conversation_summary_id: int) -> dict:
    """Return the current confidential state and append-only history for staff."""
    _require_flagged_case(conversation_summary_id)
    confidentiality = fetch_case_confidentiality(conversation_summary_id)
    if confidentiality is None:
        return {
            "confidentiality_status": NOT_CONFIDENTIAL,
            "confidentiality_reason": None,
            "created_at": None,
            "updated_at": None,
            "history": [],
        }
    return _project_confidentiality(confidentiality, conversation_summary_id)


def update_staff_case_confidentiality(
    staff_account: dict,
    conversation_summary_id: int,
    confidentiality_status: str,
    confidentiality_reason: str | None = None,
) -> dict:
    """Change current confidentiality status while appending a durable history record."""
    _require_flagged_case(conversation_summary_id)
    normalized_status = _validate_status(confidentiality_status)
    normalized_reason = _validate_reason(
        normalized_status,
        confidentiality_reason,
    )
    confidentiality = fetch_case_confidentiality(conversation_summary_id)
    if confidentiality is None:
        create_case_confidentiality(
            {
                "conversation_summary_id": conversation_summary_id,
                "staff_account_id": staff_account["id"],
                "confidentiality_status": normalized_status,
                "confidentiality_reason": normalized_reason,
            }
        )
    else:
        if confidentiality["confidentiality_status"] == normalized_status:
            raise ValueError("Case already has that confidentiality status.")
        if not update_case_confidentiality(
            conversation_summary_id,
            staff_account["id"],
            normalized_status,
            normalized_reason,
        ):
            raise LookupError("Confidentiality record not found.")

    updated_confidentiality = fetch_case_confidentiality(conversation_summary_id)
    if updated_confidentiality is None:
        raise RuntimeError("Confidentiality record could not be retrieved.")
    return _project_confidentiality(updated_confidentiality, conversation_summary_id)