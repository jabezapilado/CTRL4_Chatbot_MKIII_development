"""Deterministic final-response safety validation for chatbot output."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final, Iterable


DIAGNOSIS_OR_TREATMENT_REPLACEMENT: Final[str] = (
    "I can't provide medical or psychological diagnosis or treatment. "
    "If this concerns your well-being, please consult a qualified "
    "professional or contact the Guidance Office for appropriate support."
)
SELF_HARM_OR_VIOLENCE_REPLACEMENT: Final[str] = (
    "I'm concerned about what you've shared. Please contact a trusted "
    "person or your Guidance Office immediately if you're in immediate "
    "danger or need urgent support."
)
PROMPT_DISCLOSURE_REPLACEMENT: Final[str] = (
    "I'm unable to disclose my internal instructions, prompts, or system "
    "configuration."
)
PRIVACY_DISCLOSURE_REPLACEMENT: Final[str] = (
    "I can't disclose confidential or protected personal information."
)
FABRICATED_INSTITUTIONAL_INFORMATION_REPLACEMENT: Final[str] = (
    "I can't confirm that information. Please contact the Guidance Office "
    "or consult official university resources."
)


@dataclass(frozen=True)
class ResponseSafetyResult:
    """The final-response safety decision without retaining response content."""

    allowed: bool
    replacement: str | None = None
    category: str | None = None


class ResponseSafetyService:
    """Apply the approved deterministic post-generation safety rules."""

    _DIAGNOSIS_OR_TREATMENT: Final[re.Pattern[str]] = re.compile(
        r"\b(?:i\s+(?:diagnose|prescribe)|you\s+(?:have|are|suffer from)\s+"
        r"(?:clinical\s+)?(?:depression|anxiety|adhd|bipolar|ptsd|"
        r"a mental illness)|(?:take|stop taking)\s+[^.]{0,40}\b(?:mg|ml|"
        r"medication|medicine|prescription)|dosage)\b",
        re.IGNORECASE,
    )
    _SELF_HARM_OR_VIOLENCE: Final[re.Pattern[str]] = re.compile(
        r"\b(?:you should|i recommend|try|how to|steps to|instructions to|"
        r"ways to)\s+(?:kill|hurt|harm|injur\w*|attack\w*|stab\w*|"
        r"shoot\w*|poison\w*)\s+"
        r"(?:yourself|someone|people|another person|them)\b",
        re.IGNORECASE,
    )
    _PROMPT_DISCLOSURE: Final[re.Pattern[str]] = re.compile(
        r"\b(?:system prompt|internal instructions?|hidden instructions?|"
        r"system configuration|developer message)\b",
        re.IGNORECASE,
    )
    _PRIVACY_DISCLOSURE: Final[re.Pattern[str]] = re.compile(
        r"\b(?:account id|session id|escalation id|counselor notes?|"
        r"counsellor notes?|internal summar(?:y|ies)|database table|"
        r"database schema|database structure|internal configuration)\b",
        re.IGNORECASE,
    )
    _INSTITUTIONAL_CLAIM: Final[re.Pattern[str]] = re.compile(
        r"\b(?:guidance office|university guidance|counselor|counsellor)\b"
        r"[^.]{0,120}\b(?:official(?:ly)?|policy|policies|office hours?|"
        r"open(?:s|ing)?|close(?:d|s|ing)?|located|room|contact|email|"
        r"phone|appointment|must|required)\b",
        re.IGNORECASE,
    )
    _FACTUAL_DETAILS: Final[re.Pattern[str]] = re.compile(
        r"\b(?:[01]?\d|2[0-3]):[0-5]\d\s*(?:a\.?m\.?|p\.?m\.?)?\b|"
        r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b|"
        r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b|"
        r"\b(?:room|sjh)[ -]?\d{1,4}\b",
        re.IGNORECASE,
    )
    _UNSUPPORTED_INSTITUTION_NAMES: Final[re.Pattern[str]] = re.compile(
        r"\b(?:University Guidance Center|Student Counseling Center|"
        r"Campus Wellness Office)\b",
        re.IGNORECASE,
    )

    def validate(
        self,
        response: str,
        documents: Iterable[object] = (),
    ) -> ResponseSafetyResult:
        """Return whether a generated response may be sent unchanged."""
        text = str(response)
        documents = tuple(documents)

        if self._DIAGNOSIS_OR_TREATMENT.search(text):
            return self._blocked(
                "diagnosis_or_treatment",
                DIAGNOSIS_OR_TREATMENT_REPLACEMENT,
            )

        if self._SELF_HARM_OR_VIOLENCE.search(text):
            return self._blocked(
                "self_harm_or_violence",
                SELF_HARM_OR_VIOLENCE_REPLACEMENT,
            )

        if self._PROMPT_DISCLOSURE.search(text):
            return self._blocked(
                "prompt_disclosure",
                PROMPT_DISCLOSURE_REPLACEMENT,
            )

        if self._PRIVACY_DISCLOSURE.search(text):
            return self._blocked(
                "privacy_disclosure",
                PRIVACY_DISCLOSURE_REPLACEMENT,
            )

        if self._contains_fabricated_institutional_information(text, documents):
            return self._blocked(
                "fabricated_institutional_information",
                FABRICATED_INSTITUTIONAL_INFORMATION_REPLACEMENT,
            )

        if self._contains_unverified_institution_name(text, documents):
            return self._blocked(
                "fabricated_institutional_information",
                FABRICATED_INSTITUTIONAL_INFORMATION_REPLACEMENT,
            )

        return ResponseSafetyResult(allowed=True)

    @staticmethod
    def _blocked(category: str, replacement: str) -> ResponseSafetyResult:
        return ResponseSafetyResult(
            allowed=False,
            replacement=replacement,
            category=category,
        )

    def _contains_fabricated_institutional_information(
        self,
        response: str,
        documents: Iterable[object],
    ) -> bool:
        if not self._INSTITUTIONAL_CLAIM.search(response):
            return False

        context = "\n".join(
            str(getattr(document, "text", ""))
            for document in documents
        )
        if not context.strip():
            return True

        context_lower = context.casefold()
        details = self._FACTUAL_DETAILS.findall(response)
        return any(detail.casefold() not in context_lower for detail in details)

    def _contains_unverified_institution_name(
        self,
        response: str,
        documents: Iterable[object],
    ) -> bool:
        """Reject generic institution names absent from retrieved official context."""

        names = self._UNSUPPORTED_INSTITUTION_NAMES.findall(response)
        if not names:
            return False

        context = "\n".join(
            str(getattr(document, "text", ""))
            for document in documents
        ).casefold()
        return any(name.casefold() not in context for name in names)


__all__ = ["ResponseSafetyResult", "ResponseSafetyService"]
