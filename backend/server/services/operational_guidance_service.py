"""Student-safe answers for live Guidance Office operational information."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable, Final

from ..db import get_staff_by_program, get_student_by_id, load_persisted_settings


_OPERATIONAL_SETTING_KEYS: Final[tuple[str, ...]] = (
    "officeHours",
    "officeLocation",
    "officeEmail",
    "contactNumber",
    "appointmentAvailability",
)
_AVAILABILITY_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "officeAvailability",
        "holidays",
        "academicCalendarExclusions",
        "unavailableDates",
    }
)
_AVAILABILITY_WINDOW_FIELDS: Final[frozenset[str]] = frozenset({"days", "time"})
_SCHEDULE_FIELDS: Final[frozenset[str]] = frozenset({"room", "days", "time"})
_MAX_VALUE_LENGTH: Final[int] = 255


@dataclass(frozen=True)
class OperationalGuidanceAnswer:
    """A deterministic, source-owned operational response."""

    response: str
    source_context: str

    @property
    def text(self) -> str:
        """Provide source context to the existing response-safety projection."""
        return self.source_context


class OperationalGuidanceService:
    """Read current configured operational details without exposing staff internals."""

    def __init__(
        self,
        *,
        load_settings: Callable[[tuple[str, ...]], dict[str, Any]] = load_persisted_settings,
        fetch_student: Callable[[int], dict[str, Any] | None] = get_student_by_id,
        fetch_staff_for_program: Callable[[str], dict[str, Any] | None] = get_staff_by_program,
    ) -> None:
        self._load_settings = load_settings
        self._fetch_student = fetch_student
        self._fetch_staff_for_program = fetch_staff_for_program

    def answer(
        self,
        message: object,
        student_account: dict[str, Any] | None,
    ) -> OperationalGuidanceAnswer | None:
        """Return a live operational answer when the question requests one."""

        if not isinstance(student_account, dict) or student_account.get("role") != "student":
            return None

        text = " ".join(str(message).casefold().split())
        if not text:
            return None

        if self._is_office_hours_question(text):
            return self._office_hours_answer()
        if self._is_location_question(text):
            return self._office_location_answer()
        if self._is_contact_question(text):
            return self._contact_answer()
        if self._is_duration_question(text):
            return self._unavailable("Appointment duration")
        if self._is_counselor_question(text):
            return self._assigned_counselor_answer(student_account)
        if self._is_availability_question(text):
            return self._appointment_availability_answer(student_account)
        if self._is_booking_question(text):
            return self._booking_answer(student_account)
        return None

    def _settings(self) -> dict[str, Any]:
        return self._load_settings(_OPERATIONAL_SETTING_KEYS)

    @staticmethod
    def _safe_text(value: object) -> str | None:
        if not isinstance(value, str):
            return None
        text = " ".join(value.split())
        return text[:_MAX_VALUE_LENGTH] if text else None

    @staticmethod
    def _is_office_hours_question(text: str) -> bool:
        return bool(
            re.search(r"\b(?:office hours?|opening hours?|when .*open|oras|bukas)\b", text)
        )

    @staticmethod
    def _is_location_question(text: str) -> bool:
        return bool(
            re.search(r"\b(?:where|location|address|room|saan|nasaan)\b", text)
            and re.search(r"\b(?:guidance|office|counselor|counsellor)\b", text)
        )

    @staticmethod
    def _is_contact_question(text: str) -> bool:
        return bool(
            re.search(r"\b(?:contact|email|phone|telephone|reach|tawag|numero)\b", text)
            and (
                re.search(r"\b(?:guidance|office|counselor|counsellor)\b", text)
                or re.search(r"\b(?:your|inyo|ninyo)\s+(?:email|phone|telephone|contact)\b", text)
            )
        )

    @staticmethod
    def _is_duration_question(text: str) -> bool:
        return bool(
            re.search(r"\b(?:how long|duration|gaano katagal)\b", text)
            and re.search(r"\b(?:appointment|consultation)\b", text)
        )

    @staticmethod
    def _is_counselor_question(text: str) -> bool:
        explicit_counselor = re.search(
            r"\b(?:assigned|my|who|sino|kanino)\b", text
        ) and re.search(r"\b(?:counselor|counsellor|guidance|kausap)\b", text)
        direct_speaking_request = re.search(
            r"\b(?:who|sino)\b.*\b(?:can i )?(?:speak|talk)\b", text
        )
        return bool(explicit_counselor or direct_speaking_request)

    @staticmethod
    def _is_availability_question(text: str) -> bool:
        return bool(
            re.search(r"\b(?:available|availability|slot|slots|times?|schedule|oras|kailan)\b", text)
            and re.search(r"\b(?:appointment|consultation|counselor|counsellor|booking|book)\b", text)
        )

    @staticmethod
    def _is_booking_question(text: str) -> bool:
        return bool(re.search(r"\b(?:book|booking|appointment|mag-book)\b", text))

    def _office_hours_answer(self) -> OperationalGuidanceAnswer:
        value = self._safe_text(self._settings().get("officeHours"))
        if not value:
            return self._unavailable("Office hours")
        return self._answer(f"The current SOC Guidance Office hours are: {value}.")

    def _office_location_answer(self) -> OperationalGuidanceAnswer:
        value = self._safe_text(self._settings().get("officeLocation"))
        if not value:
            return self._unavailable("The office location")
        return self._answer(f"The current SOC Guidance Office location is: {value}.")

    def _contact_answer(self) -> OperationalGuidanceAnswer:
        settings = self._settings()
        details = [
            detail
            for detail in (
                self._safe_text(settings.get("officeEmail")),
                self._safe_text(settings.get("contactNumber")),
            )
            if detail
        ]
        if not details:
            return self._unavailable("Current Guidance Office contact details")
        return self._answer(
            "Current SOC Guidance Office contact details: " + "; ".join(details) + "."
        )

    def _student_and_counselor(
        self,
        student_account: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        try:
            student_id = int(student_account.get("id"))
        except (TypeError, ValueError):
            return {}, None
        student = self._fetch_student(student_id) or {}
        program = self._safe_text(student.get("program"))
        return student, self._fetch_staff_for_program(program) if program else None

    def _assigned_counselor_answer(
        self,
        student_account: dict[str, Any],
    ) -> OperationalGuidanceAnswer:
        _student, counselor = self._student_and_counselor(student_account)
        name = self._safe_text((counselor or {}).get("full_name"))
        if not name:
            return self._unavailable("Your assigned counselor")

        details = [f"Your currently assigned counselor is {name}"]
        office = self._safe_text((counselor or {}).get("office"))
        if office:
            details.append(f"Their listed office is {office}")
        schedule = self._format_consultation_schedule((counselor or {}).get("consultation_schedules"))
        if schedule:
            details.append(f"Their current consultation schedule is {schedule}")
        return self._answer(". ".join(details) + ".")

    def _appointment_availability_answer(
        self,
        student_account: dict[str, Any],
    ) -> OperationalGuidanceAnswer:
        availability = self._parse_availability(
            self._settings().get("appointmentAvailability")
        )
        if availability is None:
            return self._unavailable("Current appointment availability")

        _student, counselor = self._student_and_counselor(student_account)
        windows = "; ".join(
            f"{window['days']}: {window['time']}"
            for window in availability
        )
        response = (
            "The currently configured appointment availability is: "
            f"{windows}. Actual booking also checks your routed counselor's "
            "consultation schedule and existing pending or confirmed appointments."
        )
        if counselor is None:
            response += " A counselor assignment for your program is not currently available."
        return self._answer(response)

    def _booking_answer(
        self,
        student_account: dict[str, Any],
    ) -> OperationalGuidanceAnswer:
        _student, counselor = self._student_and_counselor(student_account)
        if counselor is None:
            return self._unavailable("A counselor assignment for your program")
        return self._answer(
            "Use the Appointment page to submit an appointment request. "
            "Student requests begin as pending and are checked against the "
            "current office availability and your routed counselor's consultation schedule."
        )

    @classmethod
    def _parse_availability(cls, value: object) -> list[dict[str, str]] | None:
        if isinstance(value, bytes):
            try:
                value = value.decode("utf-8")
            except UnicodeDecodeError:
                return None
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                return None
        if not isinstance(value, dict) or set(value) != _AVAILABILITY_FIELDS:
            return None
        windows = value.get("officeAvailability")
        if not isinstance(windows, list) or not windows:
            return None
        projected: list[dict[str, str]] = []
        for window in windows:
            if not isinstance(window, dict) or set(window) != _AVAILABILITY_WINDOW_FIELDS:
                return None
            days = cls._safe_text(window.get("days"))
            time = cls._safe_text(window.get("time"))
            if not days or not time:
                return None
            projected.append({"days": days, "time": time})
        return projected

    @classmethod
    def _format_consultation_schedule(cls, value: object) -> str | None:
        if isinstance(value, bytes):
            try:
                value = value.decode("utf-8")
            except UnicodeDecodeError:
                return None
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                return None
        if not isinstance(value, list):
            return None
        entries: list[str] = []
        for schedule in value:
            if not isinstance(schedule, dict) or set(schedule) != _SCHEDULE_FIELDS:
                continue
            room = cls._safe_text(schedule.get("room"))
            days = cls._safe_text(schedule.get("days"))
            time = cls._safe_text(schedule.get("time"))
            if room and days and time:
                entries.append(f"{room}, {days}, {time}")
        return "; ".join(entries) if entries else None

    @staticmethod
    def _answer(response: str) -> OperationalGuidanceAnswer:
        return OperationalGuidanceAnswer(response=response, source_context=response)

    @classmethod
    def _unavailable(cls, detail: str) -> OperationalGuidanceAnswer:
        return cls._answer(
            f"{detail} is not currently configured. Please confirm it with the SOC Guidance Office."
        )


__all__ = ["OperationalGuidanceAnswer", "OperationalGuidanceService"]
