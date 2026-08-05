"""Framework-agnostic primary-topic classification for chatbot messages."""

from __future__ import annotations

import re
from enum import Enum
from typing import Final


class Topic(str, Enum):
    APPOINTMENTS = "appointments"
    ACADEMICS = "academics"
    COUNSELING = "counseling"
    MENTAL_HEALTH = "mental_health"
    SCHOOL_SERVICES = "school_services"
    GENERAL_INQUIRY = "general_inquiry"


class TopicService:
    """Return one normalized primary topic without performing any action."""

    _APPOINTMENTS: Final[re.Pattern[str]] = re.compile(
        r"\b(?:appointment|appointments|booking|bookings|consultation|"
        r"consultations|reschedul\w*|cancel(?:led|lation|ling)?)\b"
    )
    _MENTAL_HEALTH: Final[re.Pattern[str]] = re.compile(
        r"\b(?:mental health|anxiety|anxious|depress\w*|stress\w*|"
        r"burnout|overwhelmed|panic|lonely|alone|sad|self[ -]?harm|"
        r"suicid\w*)\b"
    )
    _ACADEMICS: Final[re.Pattern[str]] = re.compile(
        r"\b(?:academic\w*|school|class|classes|grade\w*|exam\w*|quiz\w*|"
        r"study\w*|assignment\w*|project\w*|research|thesis|deadline\w*|"
        r"subject|professor|teacher|learning)\b"
    )
    _SCHOOL_SERVICES: Final[re.Pattern[str]] = re.compile(
        r"\b(?:guidance office|office hours?|opening hours?|document\w*|"
        r"clearance|certificat\w*|record\w*|form\w*|referral\w*|contact|"
        r"email|location|room|service\w*|polic\w*)\b"
    )
    _COUNSELING: Final[re.Pattern[str]] = re.compile(
        r"\b(?:counsel(?:or|ling)|guidance|relationship\w*|family|friend\w*|"
        r"career|internship|personal\s+(?:concern|support|development))\b"
    )

    def classify(self, message: str) -> str:
        """Return one normalized primary topic for *message*."""

        text = " ".join(str(message).casefold().split())

        if self._APPOINTMENTS.search(text):
            return Topic.APPOINTMENTS.value

        if self._MENTAL_HEALTH.search(text):
            return Topic.MENTAL_HEALTH.value

        if self._ACADEMICS.search(text):
            return Topic.ACADEMICS.value

        if self._SCHOOL_SERVICES.search(text):
            return Topic.SCHOOL_SERVICES.value

        if self._COUNSELING.search(text):
            return Topic.COUNSELING.value

        return Topic.GENERAL_INQUIRY.value


__all__ = ["Topic", "TopicService"]
