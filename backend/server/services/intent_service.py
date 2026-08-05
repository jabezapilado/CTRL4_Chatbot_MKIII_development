"""
Intent Detection Service

Provides deterministic, framework-agnostic intent detection for chatbot
messages. The result is internal to the conversation pipeline; it does not
perform routing, persistence, or appointment actions.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Final

from .safety_service import SafetyService


class Intent(str, Enum):
    GREETING = "greeting"
    APPOINTMENT_BOOKING = "appointment_booking"
    APPOINTMENT_CANCELLATION = "appointment_cancellation"
    APPOINTMENT_RESCHEDULING = "appointment_rescheduling"
    APPOINTMENT_HISTORY = "appointment_history"
    OFFICE_HOURS = "office_hours"
    FAQ = "faq"
    EMERGENCY = "emergency"
    UNKNOWN = "unknown"


class IntentService:
    """Classify one chatbot message using the Sprint 6 intent contract."""

    _APPOINTMENT_CONTEXT: Final[re.Pattern[str]] = re.compile(
        r"\b(?:appointment|appointments|booking|bookings|consultation|"
        r"consultations|counseling session|counselling session)\b"
    )
    _RESCHEDULE_ACTION: Final[re.Pattern[str]] = re.compile(
        r"\b(?:reschedul(?:e|ed|ing)|move|postpone|change)\b"
    )
    _CANCELLATION_ACTION: Final[re.Pattern[str]] = re.compile(
        r"\bcancel(?:led|lation|ling)?\b"
    )
    _HISTORY_REQUEST: Final[re.Pattern[str]] = re.compile(
        r"\b(?:show|view|see|list|check)\b.*\b(?:my\s+)?"
        r"(?:appointment|appointments|booking|bookings)\b|"
        r"\b(?:my|past|previous)\s+(?:appointment|appointments|"
        r"booking|bookings)\b|"
        r"\b(?:appointment|appointments|booking|bookings)\s+"
        r"(?:history|status|statuses)\b"
    )
    _BOOKING_ACTION: Final[re.Pattern[str]] = re.compile(
        r"\b(?:book|booking|schedule|scheduled|request|make|arrange|"
        r"set up|need|want)\b"
    )
    _OFFICE_HOURS_REQUEST: Final[re.Pattern[str]] = re.compile(
        r"\b(?:office hours?|opening hours?)\b|"
        r"\b(?:guidance\s+)?office\b.*\b(?:open|opening|close|closing|"
        r"hours?|schedule)\b|"
        r"\b(?:what time|when)\b.*\b(?:guidance\s+)?office\b"
    )
    _FAQ_REQUEST: Final[re.Pattern[str]] = re.compile(
        r"\b(?:faq|faqs|frequently asked questions?|help center)\b|"
        r"^(?:what|when|where|who|why|how|can|could|do|does|is|are)\b|\?$"
    )

    def detect(self, message: str) -> str:
        """Return exactly one normalized intent for *message*."""

        text = " ".join(str(message).casefold().split())

        if not text:
            return Intent.UNKNOWN.value

        if self._is_emergency(text):
            return Intent.EMERGENCY.value

        if self._is_rescheduling(text):
            return Intent.APPOINTMENT_RESCHEDULING.value

        if self._is_cancellation(text):
            return Intent.APPOINTMENT_CANCELLATION.value

        if self._HISTORY_REQUEST.search(text):
            return Intent.APPOINTMENT_HISTORY.value

        if self._is_booking(text):
            return Intent.APPOINTMENT_BOOKING.value

        if self._OFFICE_HOURS_REQUEST.search(text):
            return Intent.OFFICE_HOURS.value

        if self._FAQ_REQUEST.search(text):
            return Intent.FAQ.value

        if text in SafetyService.GREETINGS:
            return Intent.GREETING.value

        return Intent.UNKNOWN.value

    @staticmethod
    def _is_emergency(text: str) -> bool:
        """Reuse the established safety escalation vocabulary without acting on it."""

        patterns = (
            SafetyService.CRISIS_PATTERNS
            + SafetyService.DIAGNOSIS_PATTERNS
        )
        return any(re.search(pattern, text) for pattern in patterns)

    def _is_rescheduling(self, text: str) -> bool:
        if re.search(r"\breschedul(?:e|ed|ing)\b", text):
            return True

        return bool(
            self._APPOINTMENT_CONTEXT.search(text)
            and self._RESCHEDULE_ACTION.search(text)
        )

    def _is_cancellation(self, text: str) -> bool:
        return bool(
            self._CANCELLATION_ACTION.search(text)
            and self._APPOINTMENT_CONTEXT.search(text)
        )

    def _is_booking(self, text: str) -> bool:
        return bool(
            self._APPOINTMENT_CONTEXT.search(text)
            and self._BOOKING_ACTION.search(text)
        )


__all__ = ["Intent", "IntentService"]
