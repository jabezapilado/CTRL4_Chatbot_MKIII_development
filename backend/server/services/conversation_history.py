"""Safe in-memory normalization for browser conversation history.

Browser clients from earlier releases send ``{from, text}`` entries while the
prompt pipeline uses ``{role, content}``.  This module defines the latter as
the canonical, transient shape without persisting or exposing transcripts.
"""

from __future__ import annotations

from typing import Final


MAX_HISTORY_MESSAGES: Final[int] = 24
MAX_HISTORY_MESSAGE_CHARACTERS: Final[int] = 2_000

_ROLE_ALIASES: Final[dict[str, str]] = {
    "user": "user",
    "student": "user",
    "assistant": "assistant",
    "bot": "assistant",
}


def normalize_conversation_history(entries: object) -> list[dict[str, str]]:
    """Return bounded valid history in the canonical ``role``/``content`` form.

    Malformed entries and blank messages are ignored.  The original browser
    payload is never mutated, stored, or logged.
    """

    if not isinstance(entries, list):
        return []

    normalized: list[dict[str, str]] = []
    for entry in entries[-MAX_HISTORY_MESSAGES:]:
        if not isinstance(entry, dict):
            continue

        raw_role = entry.get("role", entry.get("from", ""))
        role = _ROLE_ALIASES.get(str(raw_role).strip().lower())
        if role is None:
            continue

        raw_content = entry.get("content", entry.get("text", ""))
        if not isinstance(raw_content, str):
            continue

        content = raw_content.strip()
        if not content:
            continue

        normalized.append(
            {
                "role": role,
                "content": content[:MAX_HISTORY_MESSAGE_CHARACTERS],
            }
        )

    return normalized


def summary_conversation_evidence(entries: object) -> list[dict[str, str]]:
    """Return canonical evidence beginning with the first student message."""
    evidence: list[dict[str, str]] = []
    has_student_message = False
    for item in normalize_conversation_history(entries):
        if item["role"] == "user":
            has_student_message = True
            evidence.append(item)
        elif has_student_message:
            evidence.append(item)
    return evidence


__all__ = [
    "MAX_HISTORY_MESSAGES",
    "MAX_HISTORY_MESSAGE_CHARACTERS",
    "normalize_conversation_history",
    "summary_conversation_evidence",
]
