from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import date, datetime, time, timedelta
from typing import Final

from ..db import (
    current_time,
    fetch_account_by_id,
    fetch_flagged_conversation,
    fetch_staff_inbox_summary,
    list_flagged_conversations,
    list_staff_inbox_summaries,
    list_conversation_summaries,
    list_conversation_finalizations_for_analytics,
    list_escalations_for_analytics,
    list_flagged_case_confidentiality_for_analytics,
    list_flagged_case_escalations_for_analytics,
    list_flagged_case_interventions_for_analytics,
    list_flagged_case_referrals_for_analytics,
    list_flagged_case_statuses_for_analytics,
    list_student_case_statuses,
    list_escalations,
    list_chatbot_inquiries_for_analytics,
    list_inquiries,
    mark_escalation_reviewed,
    save_conversation_summary,
    save_escalation,
    save_inquiry,
)

from . import summary_service

logger = logging.getLogger(__name__)

ESCALATION_PENDING: Final[str] = "pending"
INQUIRY_TYPE_AI_CHAT: Final[str] = "ai_chat"
ESCALATION_NORMALIZED_EMOTIONS: Final[frozenset[str]] = frozenset({
    "crisis",
    "distressed",
})


def _parse_analytics_filter_date(value: object, field_name: str) -> date | None:
    if value is None or not str(value).strip():
        return None

    try:
        return date.fromisoformat(str(value).strip())
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name}.") from exc


def _analytics_date_range(
    start_date: object,
    end_date: object,
) -> tuple[date | None, date | None, datetime | None, datetime | None]:
    start = _parse_analytics_filter_date(start_date, "start date")
    end = _parse_analytics_filter_date(end_date, "end date")

    if start and end and start > end:
        raise ValueError("Start date must not be after end date.")

    start_at = datetime.combine(start, time.min) if start else None
    end_at = (
        datetime.combine(end + timedelta(days=1), time.min)
        if end
        else None
    )
    return start, end, start_at, end_at


def _analytics_datetime(value: object) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def _message_volume(rows: list[dict]) -> dict[str, list[dict]]:
    daily: Counter[str] = Counter()
    weekly: Counter[str] = Counter()
    monthly: Counter[str] = Counter()

    for row in rows:
        created_at = _analytics_datetime(row["created_at"])
        daily[created_at.date().isoformat()] += 1
        iso_year, iso_week, _ = created_at.isocalendar()
        weekly[f"{iso_year}-W{iso_week:02d}"] += 1
        monthly[created_at.strftime("%Y-%m")] += 1

    def rows_for(counter: Counter[str], key: str) -> list[dict]:
        return [
            {key: label, "count": count}
            for label, count in sorted(counter.items())
        ]

    return {
        "daily": rows_for(daily, "date"),
        "weekly": rows_for(weekly, "week"),
        "monthly": rows_for(monthly, "month"),
    }


def get_chatbot_analytics_service(
    *,
    start_date: object = None,
    end_date: object = None,
) -> dict:
    """Return aggregate-only analytics derived from persisted chatbot records."""
    start, end, start_at, end_at = _analytics_date_range(
        start_date,
        end_date,
    )
    inquiries = list_chatbot_inquiries_for_analytics(start_at, end_at)
    finalizations = list_conversation_finalizations_for_analytics(
        start_at,
        end_at,
    )
    escalations = list_escalations_for_analytics(start_at, end_at)

    emotion_results = Counter(
        str(inquiry.get("emotion_result") or "").strip()
        for inquiry in inquiries
    )
    emotion_results.pop("", None)
    finalized_lengths = [
        int(finalization["total_messages"])
        for finalization in finalizations
    ]

    return {
        "filters": {
            "start_date": start.isoformat() if start else None,
            "end_date": end.isoformat() if end else None,
        },
        "total_chatbot_messages": len(inquiries),
        "message_volume": _message_volume(inquiries),
        "conversation_finalization_count": len(finalizations),
        "escalation_count": len(escalations),
        "persisted_emotion_result_distribution": [
            {"emotion_result": label, "count": count}
            for label, count in sorted(emotion_results.items())
        ],
        "average_finalized_conversation_length": (
            round(sum(finalized_lengths) / len(finalized_lengths), 2)
            if finalized_lengths
            else None
        ),
    }


def get_flagged_case_analytics_service(
    *,
    start_date: object = None,
    end_date: object = None,
) -> dict:
    """Return aggregate-only analytics from persisted flagged-case records."""
    start, end, start_at, end_at = _analytics_date_range(
        start_date,
        end_date,
    )
    case_statuses = list_flagged_case_statuses_for_analytics(start_at, end_at)
    referrals = list_flagged_case_referrals_for_analytics(start_at, end_at)
    interventions = list_flagged_case_interventions_for_analytics(start_at, end_at)
    confidentiality_records = list_flagged_case_confidentiality_for_analytics(
        start_at,
        end_at,
    )
    escalations = list_flagged_case_escalations_for_analytics(start_at, end_at)

    status_distribution = Counter(
        str(case.get("status") or "").strip()
        for case in case_statuses
    )
    status_distribution.pop("", None)

    return {
        "filters": {
            "start_date": start.isoformat() if start else None,
            "end_date": end.isoformat() if end else None,
        },
        "total_flagged_cases": len(case_statuses),
        "pending_flagged_case_reviews": status_distribution[ESCALATION_PENDING],
        "reviewed_flagged_cases": status_distribution["reviewed"],
        "referral_count": len(referrals),
        "intervention_count": len(interventions),
        "current_confidential_case_count": sum(
            str(record.get("confidentiality_status") or "").strip().lower()
            == "confidential"
            for record in confidentiality_records
        ),
        "escalation_trends": _message_volume(escalations),
        "persisted_case_status_distribution": [
            {"status": status, "count": count}
            for status, count in sorted(status_distribution.items())
        ],
    }

_INQUIRY_FIELDS: Final[tuple[str, ...]] = (
    "id",
    "inquiry_type",
    "emotion_result",
    "escalated",
    "appointment_recommended",
    "created_at",
)
_SUMMARY_FIELDS: Final[tuple[str, ...]] = (
    "id",
    "primary_concern",
    "conversation_type",
    "emotion_results",
    "flagged_status",
    "appointment_recommendation",
    "recommendations",
    "suggested_intervention",
    "language_used",
    "total_messages",
    "summary",
    "created_at",
)
_ESCALATION_FIELDS: Final[tuple[str, ...]] = (
    "id",
    "status",
    "intervention_notes",
    "created_at",
    "resolved_at",
)
_FLAGGED_CONVERSATION_FIELDS: Final[tuple[str, ...]] = (
    "id",
    "primary_concern",
    "conversation_type",
    "emotion_results",
    "appointment_recommendation",
    "recommendations",
    "suggested_intervention",
    "language_used",
    "total_messages",
    "summary",
    "created_at",
    "escalation_status",
    "escalation_reason",
    "reviewed_at",
)
_STUDENT_CASE_FIELDS: Final[tuple[str, ...]] = (
    "case_status",
    "submitted_at",
    "updated_at",
    "progress_text",
)
_STUDENT_CASE_STATUS_DETAILS: Final[dict[str, tuple[str, str]]] = {
    "pending": (
        "Submitted",
        "Your case has been received by the Guidance Office.",
    ),
    "reviewed": (
        "Reviewed",
        "Your case has been reviewed. The Guidance Office will contact you if further support is needed.",
    ),
}
_STAFF_INBOX_FIELDS: Final[tuple[str, ...]] = (
    "summary_id",
    "student_name",
    "student_number",
    "program",
    "primary_concern",
    "emotion_results",
    "flagged_status",
    "review_status",
    "created_at",
    "summary_preview",
    "has_referral",
    "has_intervention",
)
_STAFF_INBOX_DETAIL_FIELDS: Final[tuple[str, ...]] = (
    *_STAFF_INBOX_FIELDS,
    "summary",
    "recommendations",
    "suggested_intervention",
    "language_used",
    "total_messages",
    "escalation_status",
    "escalation_reason",
)


def _project_fields(row: dict, fields: tuple[str, ...]) -> dict:
    return {field: row.get(field) for field in fields}


def _staff_assigned_programs(staff_account: dict) -> set[str]:
    account = fetch_account_by_id(int(staff_account["id"]), role="staff")
    if not account:
        return set()

    programs = account.get("assigned_programs")
    if isinstance(programs, bytes):
        try:
            programs = programs.decode("utf-8")
        except UnicodeDecodeError:
            return set()
    if isinstance(programs, str):
        try:
            programs = json.loads(programs)
        except json.JSONDecodeError:
            return set()
    if not isinstance(programs, list):
        return set()
    return {
        str(program).strip().casefold()
        for program in programs
        if str(program).strip()
    }


def _inbox_review_status(row: dict) -> str:
    escalation_status = str(row.get("escalation_status") or "").strip().lower()
    if escalation_status in {"pending", "reviewed"}:
        return escalation_status
    return "routine"


def _summary_preview(value: object) -> str:
    text = " ".join(str(value or "").split())
    if not text:
        return (
            "An AI summary could not be generated. Review the available case "
            "metadata and contact the student through the approved Guidance Office process."
        )
    return text[:240] + ("..." if len(text) > 240 else "")


def _project_staff_inbox_row(row: dict, *, detail: bool = False) -> dict:
    projected = {
        "summary_id": row.get("summary_id"),
        "student_name": row.get("student_name"),
        "student_number": row.get("student_number"),
        "program": row.get("program"),
        "primary_concern": row.get("primary_concern"),
        "emotion_results": row.get("emotion_results"),
        "flagged_status": bool(row.get("flagged_status")),
        "review_status": _inbox_review_status(row),
        "created_at": row.get("created_at"),
        "summary_preview": _summary_preview(row.get("summary")),
        "has_referral": bool(row.get("has_referral")),
        "has_intervention": bool(row.get("has_intervention")),
    }
    if detail:
        projected.update(
            {
                "summary": row.get("summary") or (
                    "An AI summary could not be generated. Review the available case "
                    "metadata and contact the student through the approved Guidance Office process."
                ),
                "recommendations": row.get("recommendations"),
                "suggested_intervention": row.get("suggested_intervention"),
                "language_used": row.get("language_used"),
                "total_messages": row.get("total_messages"),
                "escalation_status": row.get("escalation_status"),
                "escalation_reason": row.get("escalation_reason"),
            }
        )
    return _project_fields(
        projected,
        _STAFF_INBOX_DETAIL_FIELDS if detail else _STAFF_INBOX_FIELDS,
    )


def list_staff_inbox_items(staff_account: dict) -> list[dict]:
    """Return one current finalized, reviewable summary per authorized student."""
    programs = _staff_assigned_programs(staff_account)
    if not programs:
        return []

    rows = list_staff_inbox_summaries(sorted(programs))
    # The database query groups by account; preserve a service-owned final guard
    # in case legacy data or a future join ever returns a duplicate summary row.
    unique: dict[object, dict] = {}
    for row in rows:
        student_key = row.get("student_account_id") or row.get("student_number")
        if not student_key:
            continue
        unique.setdefault(student_key, row)
    return [_project_staff_inbox_row(row) for row in unique.values()]


def get_staff_inbox_item(staff_account: dict, summary_id: int) -> dict | None:
    row = fetch_staff_inbox_summary(summary_id)
    if row is None:
        return None
    programs = _staff_assigned_programs(staff_account)
    if str(row.get("program") or "").strip().casefold() not in programs:
        return None
    return _project_staff_inbox_row(row, detail=True)


def list_staff_inquiries() -> list[dict]:
    """Return the staff-permitted inquiry history without account linkage data."""
    return [_project_fields(row, _INQUIRY_FIELDS) for row in list_inquiries()]


def list_staff_conversation_summaries() -> list[dict]:
    """Return the staff-permitted counselor summaries without account linkage data."""
    return [
        _project_fields(row, _SUMMARY_FIELDS)
        for row in list_conversation_summaries()
    ]


def list_staff_escalations() -> list[dict]:
    """Return the staff-permitted escalations without internal linkage data."""
    return [_project_fields(row, _ESCALATION_FIELDS) for row in list_escalations()]


def determine_escalation_reason(
    *,
    escalated: bool,
    normalized_emotion: str | None,
) -> str | None:
    """Return the existing AI trigger reason without changing escalation policy."""
    normalized_emotion = str(normalized_emotion or "").strip().lower()
    if normalized_emotion in ESCALATION_NORMALIZED_EMOTIONS:
        return f"Detected {normalized_emotion} emotion."
    if escalated:
        return "AI safety escalation."
    return None


def list_staff_flagged_conversations() -> list[dict]:
    """Return staff-visible flagged conversation summaries only."""
    return [
        _project_fields(row, _FLAGGED_CONVERSATION_FIELDS)
        for row in list_flagged_conversations()
    ]


def list_student_cases(student_account: dict) -> list[dict]:
    """Return only the authenticated student's approved case-status fields."""
    cases = []
    for row in list_student_case_statuses(student_account["id"]):
        case_status, progress_text = _STUDENT_CASE_STATUS_DETAILS.get(
            str(row.get("escalation_status") or "").strip().lower(),
            (
                "In Progress",
                "Your case is being handled by the Guidance Office.",
            ),
        )
        cases.append(
            {
                "case_status": case_status,
                "submitted_at": row.get("submitted_at"),
                "updated_at": row.get("updated_at"),
                "progress_text": progress_text,
            }
        )
    return [_project_fields(case, _STUDENT_CASE_FIELDS) for case in cases]


def get_staff_flagged_conversation(summary_id: int) -> dict | None:
    """Return one staff-visible flagged conversation summary."""
    row = fetch_flagged_conversation(summary_id)
    if row is None:
        return None

    return _project_fields(row, _FLAGGED_CONVERSATION_FIELDS)


def mark_staff_flagged_conversation_reviewed(summary_id: int) -> dict | None:
    """Mark a pending flagged conversation as reviewed without altering history."""
    conversation = get_staff_flagged_conversation(summary_id)
    if conversation is None:
        return None

    if conversation["escalation_status"] == "reviewed":
        return conversation
    if conversation["escalation_status"] != ESCALATION_PENDING:
        raise ValueError("Flagged conversation cannot be marked as reviewed.")
    if not mark_escalation_reviewed(summary_id):
        raise ValueError("Flagged conversation cannot be marked as reviewed.")

    return get_staff_flagged_conversation(summary_id)


def record_chat_inquiry(
    *,
    account_id: int,
    emotion: str,
    escalated: bool,
) -> None:
    """Persist the metadata generated by a successful chatbot response."""
    save_inquiry(
        {
            "account_id": account_id,
            "inquiry_type": INQUIRY_TYPE_AI_CHAT,
            "emotion_result": emotion,
            "escalated": escalated,
            "appointment_recommended": False,
            "created_at": current_time(),
        }
    )


def should_escalate_conversation(
    *,
    escalated: bool,
    normalized_emotion: str | None,
) -> bool:
    """Decide whether Conversation Intelligence marks a session for escalation."""
    return (
        escalated
        or str(normalized_emotion or "").lower()
        in ESCALATION_NORMALIZED_EMOTIONS
    )


def _save_escalation(
    summary_id: int,
    account_id: int,
    escalation_reason: str,
) -> None:
    save_escalation(
        {
            "account_id": account_id,
            "summary_id": summary_id,
            "status": ESCALATION_PENDING,
            "escalation_reason": escalation_reason,
            "created_at": current_time(),
        }
    )


def finalize_conversation(
    *,
    user: dict,
    conversation: list[dict],
    topic: str,
    language: str,
    emotion: str,
    flagged: bool,
    escalation_reason: str | None = None,
) -> dict:
    logger.info("Conversation finalization started (flagged=%s).", flagged)
    summary = summary_service.generate_summary(
        student_name=user["full_name"],
        conversation=conversation,
        topic=topic,
        language=language,
        emotion=emotion,
        flagged=flagged,
    )

    summary_id = save_conversation_summary(
        {
            "account_id": user["id"],
            "primary_concern": summary.primary_concern,
            "conversation_type": summary.conversation_type,
            "emotion_results": summary.emotion,
            "flagged_status": summary.flagged,
            "appointment_recommendation": summary.appointment_recommendation,
            "recommendations": summary.recommendations,
            "suggested_intervention": summary.suggested_intervention,
            "language_used": summary.language,
            "total_messages": summary.total_messages,
            "summary": summary.summary,
            "created_at": current_time(),
        }
    )

    if summary.flagged:
        _save_escalation(
            summary_id,
            user["id"],
            escalation_reason
            or determine_escalation_reason(
                escalated=True,
                normalized_emotion=summary.emotion,
            )
            or "AI safety escalation.",
        )

    logger.info("Conversation finalization completed.")

    return {
        "success": True,
        "summary_id": summary_id,
    }
