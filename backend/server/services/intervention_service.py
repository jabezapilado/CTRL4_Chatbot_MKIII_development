from __future__ import annotations

from typing import Final

from ..db import (
    create_intervention,
    fetch_flagged_conversation,
    fetch_intervention,
    list_intervention_history,
    list_interventions,
    record_intervention_outcome,
    update_intervention_progress,
)


INTERVENTION_TYPES: Final[frozenset[str]] = frozenset({
    "Counseling Session",
    "Follow-up Meeting",
    "Wellness Check",
    "Academic Intervention",
    "External Referral Follow-up",
})
INTERVENTION_PROGRESS_STATUSES: Final[frozenset[str]] = frozenset({
    "planned",
    "ongoing",
    "completed",
    "discontinued",
})
TERMINAL_INTERVENTION_STATUSES: Final[frozenset[str]] = frozenset({
    "completed",
    "discontinued",
})
INITIAL_INTERVENTION_PROGRESS_STATUS: Final[str] = "planned"
MAX_INTERVENTION_OBJECTIVE_LENGTH: Final[int] = 5000
MAX_INTERVENTION_OUTCOME_LENGTH: Final[int] = 5000
_INTERVENTION_FIELDS: Final[tuple[str, ...]] = (
    "id",
    "intervention_type",
    "objective",
    "progress_status",
    "outcome",
    "created_at",
    "updated_at",
)
_HISTORY_FIELDS: Final[tuple[str, ...]] = (
    "progress_status",
    "outcome",
    "created_at",
)


def _project_fields(record: dict, fields: tuple[str, ...]) -> dict:
    return {field: record.get(field) for field in fields}


def _require_flagged_case(conversation_summary_id: int) -> None:
    if fetch_flagged_conversation(conversation_summary_id) is None:
        raise LookupError("Flagged conversation not found.")


def _validate_intervention_type(intervention_type: str) -> str:
    normalized_type = str(intervention_type or "").strip()
    if normalized_type not in INTERVENTION_TYPES:
        raise ValueError("Intervention type is not supported.")
    return normalized_type


def _validate_progress_status(progress_status: str) -> str:
    normalized_status = str(progress_status or "").strip().lower()
    if normalized_status not in INTERVENTION_PROGRESS_STATUSES:
        raise ValueError("Intervention progress status is not supported.")
    return normalized_status


def _validate_text(value: str, label: str, maximum_length: int) -> str:
    normalized_value = str(value or "").strip()
    if not normalized_value:
        raise ValueError(f"Intervention {label} is required.")
    if len(normalized_value) > maximum_length:
        raise ValueError(
            f"Intervention {label} must not exceed {maximum_length} characters."
        )
    return normalized_value


def _project_intervention(
    intervention: dict,
    conversation_summary_id: int,
) -> dict:
    projected_intervention = _project_fields(intervention, _INTERVENTION_FIELDS)
    projected_intervention["history"] = [
        _project_fields(item, _HISTORY_FIELDS)
        for item in list_intervention_history(
            projected_intervention["id"],
            conversation_summary_id,
        )
    ]
    return projected_intervention


def list_staff_interventions(conversation_summary_id: int) -> list[dict]:
    """Return staff-visible intervention records and append-only history."""
    _require_flagged_case(conversation_summary_id)
    return [
        _project_intervention(intervention, conversation_summary_id)
        for intervention in list_interventions(conversation_summary_id)
    ]


def create_staff_intervention(
    staff_account: dict,
    conversation_summary_id: int,
    intervention_type: str,
    objective: str,
) -> dict:
    """Create a planned intervention for an existing flagged conversation."""
    _require_flagged_case(conversation_summary_id)
    normalized_type = _validate_intervention_type(intervention_type)
    normalized_objective = _validate_text(
        objective,
        "objective",
        MAX_INTERVENTION_OBJECTIVE_LENGTH,
    )
    intervention_id = create_intervention(
        {
            "conversation_summary_id": conversation_summary_id,
            "staff_account_id": staff_account["id"],
            "intervention_type": normalized_type,
            "objective": normalized_objective,
            "progress_status": INITIAL_INTERVENTION_PROGRESS_STATUS,
        }
    )
    intervention = fetch_intervention(intervention_id, conversation_summary_id)
    if intervention is None:
        raise RuntimeError("Intervention could not be retrieved.")
    return _project_intervention(intervention, conversation_summary_id)


def update_staff_intervention_progress(
    staff_account: dict,
    conversation_summary_id: int,
    intervention_id: int,
    progress_status: str,
) -> dict:
    """Update progress while retaining every prior progress record."""
    _require_flagged_case(conversation_summary_id)
    normalized_status = _validate_progress_status(progress_status)
    intervention = fetch_intervention(intervention_id, conversation_summary_id)
    if intervention is None:
        raise LookupError("Intervention not found.")
    if intervention["outcome"] is not None:
        raise ValueError("Intervention progress cannot change after recording an outcome.")
    if intervention["progress_status"] == normalized_status:
        raise ValueError("Intervention already has that progress status.")
    if not update_intervention_progress(
        intervention_id,
        conversation_summary_id,
        staff_account["id"],
        normalized_status,
    ):
        raise LookupError("Intervention not found.")
    updated_intervention = fetch_intervention(intervention_id, conversation_summary_id)
    if updated_intervention is None:
        raise RuntimeError("Intervention could not be retrieved.")
    return _project_intervention(updated_intervention, conversation_summary_id)


def record_staff_intervention_outcome(
    staff_account: dict,
    conversation_summary_id: int,
    intervention_id: int,
    outcome: str,
) -> dict:
    """Record one outcome only after an intervention reaches a terminal status."""
    _require_flagged_case(conversation_summary_id)
    normalized_outcome = _validate_text(
        outcome,
        "outcome",
        MAX_INTERVENTION_OUTCOME_LENGTH,
    )
    intervention = fetch_intervention(intervention_id, conversation_summary_id)
    if intervention is None:
        raise LookupError("Intervention not found.")
    if intervention["progress_status"] not in TERMINAL_INTERVENTION_STATUSES:
        raise ValueError(
            "Intervention outcome can be recorded only after completion or discontinuation."
        )
    if intervention["outcome"] is not None:
        raise ValueError("Intervention outcome has already been recorded.")
    if not record_intervention_outcome(
        intervention_id,
        conversation_summary_id,
        staff_account["id"],
        intervention["progress_status"],
        normalized_outcome,
    ):
        raise LookupError("Intervention not found.")
    updated_intervention = fetch_intervention(intervention_id, conversation_summary_id)
    if updated_intervention is None:
        raise RuntimeError("Intervention could not be retrieved.")
    return _project_intervention(updated_intervention, conversation_summary_id)