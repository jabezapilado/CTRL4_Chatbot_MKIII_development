"""Read-only structured metadata extraction for chatbot messages."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Final


@dataclass(frozen=True)
class ConversationMetadata:
    student_number: str | None = None
    appointment_date: str | None = None
    appointment_time: str | None = None
    office: str | None = None
    counselor: str | None = None
    category: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


class MetadataExtractionService:
    """Extract explicit message metadata without resolving or persisting it."""

    _STUDENT_NUMBER: Final[re.Pattern[str]] = re.compile(r"\b\d{4}-\d{5}\b")
    _DATE: Final[re.Pattern[str]] = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
    _TWELVE_HOUR_TIME: Final[re.Pattern[str]] = re.compile(
        r"\b(?:0?[1-9]|1[0-2]):[0-5]\d\s*(?:a\.?m\.?|p\.?m\.?)\b",
        re.IGNORECASE,
    )
    _TWENTY_FOUR_HOUR_TIME: Final[re.Pattern[str]] = re.compile(
        r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b"
    )
    _GUIDANCE_OFFICE: Final[re.Pattern[str]] = re.compile(
        r"\b(?:soc\s+)?guidance office\b",
        re.IGNORECASE,
    )
    _COUNSELOR: Final[re.Pattern[str]] = re.compile(
        r"\b(?i:counselor|counsellor)\s+"
        r"(?P<name>[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b"
    )
    _CATEGORIES: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
        ("home_family", re.compile(r"\bhome and family\b", re.IGNORECASE)),
        (
            "relationships",
            re.compile(
                r"\brelationships? with peers?/opposite sex\b",
                re.IGNORECASE,
            ),
        ),
        (
            "personality",
            re.compile(r"\bpersonality development\b", re.IGNORECASE),
        ),
        (
            "career_schooling",
            re.compile(r"\bcareer/schooling\b", re.IGNORECASE),
        ),
        (
            "religion",
            re.compile(r"\breligion/spiritual development\b", re.IGNORECASE),
        ),
        (
            "health",
            re.compile(r"\bhealth and recreation\b", re.IGNORECASE),
        ),
        ("employment", re.compile(r"\bemployment\b", re.IGNORECASE)),
    )

    def extract(self, message: str) -> ConversationMetadata:
        """Return explicit metadata candidates found in *message*."""

        text = str(message).strip()

        return ConversationMetadata(
            student_number=self._extract_match(self._STUDENT_NUMBER, text),
            appointment_date=self._extract_date(text),
            appointment_time=self._extract_time(text),
            office=(
                "Guidance Office"
                if self._GUIDANCE_OFFICE.search(text)
                else None
            ),
            counselor=self._extract_counselor(text),
            category=self._extract_category(text),
        )

    @staticmethod
    def _extract_match(pattern: re.Pattern[str], text: str) -> str | None:
        match = pattern.search(text)
        return match.group(0) if match else None

    def _extract_date(self, text: str) -> str | None:
        value = self._extract_match(self._DATE, text)
        if not value:
            return None

        try:
            return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
        except ValueError:
            return None

    def _extract_time(self, text: str) -> str | None:
        value = self._extract_match(self._TWELVE_HOUR_TIME, text)
        if value:
            normalized = value.upper().replace(".", "")
            return datetime.strptime(normalized, "%I:%M %p").strftime("%I:%M %p")

        value = self._extract_match(self._TWENTY_FOUR_HOUR_TIME, text)
        if value:
            return datetime.strptime(value, "%H:%M").strftime("%I:%M %p")

        return None

    def _extract_counselor(self, text: str) -> str | None:
        match = self._COUNSELOR.search(text)
        return match.group("name") if match else None

    def _extract_category(self, text: str) -> str | None:
        for category, pattern in self._CATEGORIES:
            if pattern.search(text):
                return category

        return None


__all__ = ["ConversationMetadata", "MetadataExtractionService"]
