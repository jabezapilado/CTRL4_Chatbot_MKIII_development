"""Validated, persisted application settings and appointment projections."""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Callable, Final

from ..db import load_persisted_settings


OFFICE_SETTING_KEYS: Final[tuple[str, ...]] = (
    "officeName",
    "officeHours",
    "officeEmail",
    "contactNumber",
    "officeLocation",
)
APPOINTMENT_AVAILABILITY_KEY: Final[str] = "appointmentAvailability"
FAQ_SETTING_KEY: Final[str] = "faqs"
SUPPORTED_SETTING_KEYS: Final[frozenset[str]] = frozenset(
    (*OFFICE_SETTING_KEYS, APPOINTMENT_AVAILABILITY_KEY)
)
APPOINTMENT_AVAILABILITY_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "bookingEnabled",
        "officeAvailability",
        "holidays",
        "academicCalendarExclusions",
        "unavailableDates",
        "appointmentCategories",
        "consultationModes",
    }
)
LEGACY_AVAILABILITY_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "officeAvailability",
        "holidays",
        "academicCalendarExclusions",
        "unavailableDates",
    }
)
WEEKDAY_NAMES: Final[tuple[str, ...]] = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)
WEEKDAY_INDEXES: Final[dict[str, int]] = {
    name.casefold(): index for index, name in enumerate(WEEKDAY_NAMES)
}
MAX_TEXT_LENGTH: Final[int] = 255
MAX_CHOICE_LENGTH: Final[int] = 80
MAX_FAQ_ANSWER_LENGTH: Final[int] = 2_000
APPROVED_OFFICE_SETTINGS: Final[dict[str, str]] = {
    "officeName": "SOC Guidance Office",
    "officeHours": "Monday to Friday, 7:00 AM to 5:00 PM",
    "officeEmail": "guidance@hau.edu.ph",
    "officeLocation": "Holy Angel University",
    "contactNumber": "",
}
APPROVED_APPOINTMENT_AVAILABILITY: Final[dict[str, Any]] = {
    "bookingEnabled": True,
    "officeAvailability": [
        {"days": day, "time": "07:00 AM - 05:00 PM"}
        for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
    ],
    "holidays": [],
    "academicCalendarExclusions": [],
    "unavailableDates": [],
    "appointmentCategories": [
        "Home and Family",
        "Relationships with Peers/Opposite Sex",
        "Personality Development",
        "Career / Schooling",
        "Religion / Spiritual Development",
        "Health and Recreation",
        "Employment",
        "Others",
    ],
    "consultationModes": ["Online", "Onsite"],
}
APPROVED_FAQS: Final[tuple[dict[str, Any], ...]] = (
    {
        "id": "office-hours",
        "title": "Office Hours",
        "question": "What are your office hours?",
        "answer": "The SOC Guidance Office is open from Monday to Friday, 7:00 AM to 5:00 PM.",
        "active": True,
        "order": 1,
    },
    {
        "id": "book-appointment",
        "title": "Book Appointment",
        "question": "How can I book an appointment?",
        "answer": "You may book an appointment by selecting the Book Appointment option and submitting your preferred date, time, appointment category, consultation mode, contact number, and reason for the appointment.",
        "active": True,
        "order": 2,
    },
    {
        "id": "counseling-services",
        "title": "Counseling Services",
        "question": "Can I speak with a counselor?",
        "answer": "Yes. You may request counseling assistance through the chatbot or visit the SOC Guidance Office during office hours.",
        "active": True,
        "order": 3,
    },
)


def _decode_json(value: object) -> object:
    if isinstance(value, bytes):
        try:
            value = value.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Invalid settings value.") from exc
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _save_persisted_settings(settings: dict[str, Any]) -> None:
    """Resolve the write helper only for staff-initiated settings updates."""
    from ..db import save_settings

    save_settings(settings)


def _normalize_text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be text.")
    normalized = " ".join(value.split())
    if len(normalized) > MAX_TEXT_LENGTH:
        raise ValueError(f"{field_name} is too long.")
    return normalized


def _normalize_faq_text(value: object, field_name: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"FAQ {field_name} must be text.")
    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError(f"FAQ {field_name} is required.")
    if len(normalized) > maximum:
        raise ValueError(f"FAQ {field_name} is too long.")
    return normalized


def _legacy_faq_id(title: str, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-")
    return f"legacy-{slug or 'faq'}-{index + 1}"


def _normalize_faq_entry(value: object, index: int) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("Each FAQ entry must be an object.")
    title = _normalize_faq_text(value.get("title"), "title", MAX_TEXT_LENGTH)
    question = _normalize_faq_text(value.get("question"), "question", MAX_TEXT_LENGTH)
    answer = _normalize_faq_text(value.get("answer"), "answer", MAX_FAQ_ANSWER_LENGTH)
    identifier = value.get("id")
    if identifier is None:
        identifier = _legacy_faq_id(title, index)
    if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", identifier):
        raise ValueError("FAQ identifier is invalid.")
    active = value.get("active", True)
    if not isinstance(active, bool):
        raise ValueError("FAQ active status must be true or false.")
    order = value.get("order", index + 1)
    if not isinstance(order, int) or isinstance(order, bool) or order < 0:
        raise ValueError("FAQ order is invalid.")
    return {
        "id": identifier,
        "title": title,
        "question": question,
        "answer": answer,
        "active": active,
        "order": order,
    }


def normalize_faq_entries(value: object) -> list[dict[str, Any]]:
    entries = _decode_json(value)
    if not isinstance(entries, list):
        raise ValueError("FAQs must be a list.")
    normalized = [_normalize_faq_entry(entry, index) for index, entry in enumerate(entries)]
    identifiers = [entry["id"] for entry in normalized]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("FAQ identifiers must be unique.")
    return sorted(normalized, key=lambda entry: (entry["order"], entry["id"]))


@dataclass(frozen=True)
class FAQAnswer:
    response: str
    source_context: str


def _normalize_date(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must contain ISO dates.")
    try:
        return date.fromisoformat(value.strip()).isoformat()
    except ValueError as exc:
        raise ValueError(f"{field_name} must contain ISO dates.") from exc


def _normalize_date_list(value: object, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list of ISO dates.")
    normalized = [_normalize_date(item, field_name) for item in value]
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{field_name} must not contain duplicate dates.")
    return normalized


def _normalize_days(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Availability days must be text.")
    days = " ".join(value.split())
    lower_days = days.casefold()
    if " to " in lower_days:
        start_text, end_text = re.split(r"\s+to\s+", days, maxsplit=1, flags=re.I)
    elif "-" in days:
        parts = days.split("-")
        if len(parts) != 2:
            raise ValueError("Availability days are invalid.")
        start_text, end_text = (part.strip() for part in parts)
    else:
        index = WEEKDAY_INDEXES.get(lower_days)
        if index is None:
            raise ValueError("Availability days are invalid.")
        return WEEKDAY_NAMES[index]

    start_index = WEEKDAY_INDEXES.get(start_text.strip().casefold())
    end_index = WEEKDAY_INDEXES.get(end_text.strip().casefold())
    if start_index is None or end_index is None or start_index > end_index:
        raise ValueError("Availability days are invalid.")
    return f"{WEEKDAY_NAMES[start_index]} to {WEEKDAY_NAMES[end_index]}"


def _normalize_time(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Availability time is invalid.")
    try:
        return datetime.strptime(" ".join(value.split()), "%I:%M %p").strftime(
            "%I:%M %p"
        )
    except ValueError as exc:
        raise ValueError("Availability time is invalid.") from exc


def _time_minutes(value: str) -> int:
    parsed = datetime.strptime(value, "%I:%M %p")
    return parsed.hour * 60 + parsed.minute


def _normalize_time_range(value: object) -> str:
    if not isinstance(value, str) or value.count("-") != 1:
        raise ValueError("Availability time must be a start and end time.")
    start_text, end_text = (part.strip() for part in value.split("-"))
    start_time = _normalize_time(start_text)
    end_time = _normalize_time(end_text)
    if _time_minutes(start_time) >= _time_minutes(end_time):
        raise ValueError("Availability end time must be after start time.")
    return f"{start_time} - {end_time}"


def _normalize_windows(
    value: object,
    *,
    required: bool,
) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError("Office availability must be a list of windows.")
    if required and not value:
        raise ValueError("Office availability must contain at least one window.")
    normalized: list[dict[str, str]] = []
    for window in value:
        if not isinstance(window, dict) or set(window) != {"days", "time"}:
            raise ValueError("Each office availability window is invalid.")
        normalized.append(
            {
                "days": _normalize_days(window["days"]),
                "time": _normalize_time_range(window["time"]),
            }
        )
    if len({(window["days"], window["time"]) for window in normalized}) != len(normalized):
        raise ValueError("Office availability must not contain duplicate windows.")
    return normalized


def _normalize_choices(
    value: object,
    field_name: str,
    *,
    required: bool,
) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list of choices.")
    if required and not value:
        raise ValueError(f"{field_name} must contain at least one choice.")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{field_name} must contain text choices.")
        choice = " ".join(item.split())
        if not choice or len(choice) > MAX_CHOICE_LENGTH:
            raise ValueError(f"{field_name} contains an invalid choice.")
        normalized.append(choice)
    if len({choice.casefold() for choice in normalized}) != len(normalized):
        raise ValueError(f"{field_name} must not contain duplicate choices.")
    return normalized


def normalize_appointment_availability(
    value: object,
    *,
    allow_legacy: bool = False,
) -> dict[str, Any]:
    """Validate and normalize persisted appointment configuration."""
    availability = _decode_json(value)
    if not isinstance(availability, dict):
        raise ValueError("Appointment availability must be an object.")

    fields = set(availability)
    is_legacy = fields == LEGACY_AVAILABILITY_FIELDS
    if fields != APPOINTMENT_AVAILABILITY_FIELDS and not (allow_legacy and is_legacy):
        raise ValueError("Appointment availability contains unsupported fields.")

    booking_enabled = availability.get("bookingEnabled", True)
    if not isinstance(booking_enabled, bool):
        raise ValueError("Booking enabled must be true or false.")

    normalized: dict[str, Any] = {
        "officeAvailability": _normalize_windows(
            availability.get("officeAvailability"),
            required=booking_enabled,
        ),
        "holidays": _normalize_date_list(availability.get("holidays"), "Holidays"),
        "academicCalendarExclusions": _normalize_date_list(
            availability.get("academicCalendarExclusions"),
            "Academic calendar exclusions",
        ),
        "unavailableDates": _normalize_date_list(
            availability.get("unavailableDates"),
            "Unavailable dates",
        ),
    }
    if is_legacy:
        normalized["bookingEnabled"] = booking_enabled
        normalized["appointmentCategories"] = None
        normalized["consultationModes"] = None
        return normalized

    normalized["bookingEnabled"] = booking_enabled
    normalized["appointmentCategories"] = _normalize_choices(
        availability.get("appointmentCategories"),
        "Appointment categories",
        required=booking_enabled,
    )
    normalized["consultationModes"] = _normalize_choices(
        availability.get("consultationModes"),
        "Consultation modes",
        required=booking_enabled,
    )
    return normalized


class SettingsService:
    """Own settings validation and public projections outside Flask routes."""

    def __init__(
        self,
        *,
        load: Callable[[tuple[str, ...]], dict[str, Any]] = load_persisted_settings,
        save: Callable[[dict[str, Any]], None] = _save_persisted_settings,
    ) -> None:
        self._load = load
        self._save = save

    def get_settings(self) -> dict[str, Any]:
        persisted = self._load((*OFFICE_SETTING_KEYS, APPOINTMENT_AVAILABILITY_KEY))
        settings = {
            key: _normalize_text(persisted[key], key) if key in persisted else ""
            for key in OFFICE_SETTING_KEYS
        }
        try:
            availability = normalize_appointment_availability(
                persisted.get(APPOINTMENT_AVAILABILITY_KEY),
                allow_legacy=True,
            )
        except ValueError:
            availability = None
        settings[APPOINTMENT_AVAILABILITY_KEY] = availability
        if availability and not availability["bookingEnabled"]:
            settings["appointmentConfigurationState"] = "booking_disabled"
        elif (
            availability
            and availability["appointmentCategories"] is not None
            and availability["consultationModes"] is not None
        ):
            settings["appointmentConfigurationState"] = "configured"
        else:
            settings["appointmentConfigurationState"] = "unconfigured"
        return settings

    def seed_approved_mk_ii_settings(self) -> dict[str, list[str]]:
        """Seed approved operational values without replacing persisted staff edits."""
        persisted = self._load(
            (*OFFICE_SETTING_KEYS, APPOINTMENT_AVAILABILITY_KEY, FAQ_SETTING_KEY)
        )
        seeded: dict[str, Any] = {}
        preserved: list[str] = []
        for key, value in APPROVED_OFFICE_SETTINGS.items():
            is_unconfigured = key not in persisted or (
                key != "contactNumber" and not str(persisted[key]).strip()
            )
            if is_unconfigured:
                seeded[key] = value
            else:
                preserved.append(key)
        if APPOINTMENT_AVAILABILITY_KEY not in persisted:
            seeded[APPOINTMENT_AVAILABILITY_KEY] = APPROVED_APPOINTMENT_AVAILABILITY
        else:
            preserved.append(APPOINTMENT_AVAILABILITY_KEY)
        if FAQ_SETTING_KEY not in persisted:
            seeded[FAQ_SETTING_KEY] = list(APPROVED_FAQS)
        else:
            preserved.append(FAQ_SETTING_KEY)
        if seeded:
            self._save(seeded)
        return {"seeded": sorted(seeded), "preserved": sorted(preserved)}

    def update_settings(self, payload: object) -> None:
        if not isinstance(payload, dict) or not payload:
            raise ValueError("Settings payload is required.")
        unsupported = set(payload) - SUPPORTED_SETTING_KEYS
        if unsupported:
            raise ValueError("Unsupported settings were provided.")

        normalized: dict[str, Any] = {}
        for key in OFFICE_SETTING_KEYS:
            if key in payload:
                normalized[key] = _normalize_text(payload[key], key)
        if APPOINTMENT_AVAILABILITY_KEY in payload:
            normalized[APPOINTMENT_AVAILABILITY_KEY] = normalize_appointment_availability(
                payload[APPOINTMENT_AVAILABILITY_KEY]
            )
        self._save(normalized)

    def list_faqs(self) -> list[dict[str, Any]]:
        persisted = self._load((FAQ_SETTING_KEY,))
        if FAQ_SETTING_KEY not in persisted:
            return []
        return normalize_faq_entries(persisted[FAQ_SETTING_KEY])

    def create_faq(self, payload: object) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("FAQ payload is required.")
        entries = self.list_faqs()
        entry = _normalize_faq_entry(
            {
                "id": uuid.uuid4().hex,
                "title": payload.get("title"),
                "question": payload.get("question"),
                "answer": payload.get("answer"),
                "active": payload.get("active", True),
                "order": payload.get("order", max((item["order"] for item in entries), default=0) + 1),
            },
            len(entries),
        )
        entries.append(entry)
        self._save({FAQ_SETTING_KEY: entries})
        return entry

    def update_faq(self, identifier: str, payload: object) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("FAQ payload is required.")
        entries = self.list_faqs()
        for index, entry in enumerate(entries):
            if entry["id"] != identifier:
                continue
            updated = _normalize_faq_entry(
                {
                    **entry,
                    **{
                        key: value
                        for key, value in payload.items()
                        if key in {"title", "question", "answer", "active", "order"}
                    },
                },
                index,
            )
            entries[index] = updated
            self._save({FAQ_SETTING_KEY: entries})
            return updated
        raise LookupError("FAQ entry not found.")

    def remove_faq(self, identifier: str) -> None:
        entries = self.list_faqs()
        remaining = [entry for entry in entries if entry["id"] != identifier]
        if len(remaining) == len(entries):
            raise LookupError("FAQ entry not found.")
        self._save({FAQ_SETTING_KEY: remaining})

    def answer_faq(
        self,
        message: object,
        student_account: dict[str, Any] | None,
    ) -> FAQAnswer | None:
        if not isinstance(student_account, dict) or student_account.get("role") != "student":
            return None
        text = " ".join(str(message).casefold().split())
        if not text:
            return None
        matched: tuple[int, dict[str, Any]] | None = None
        message_words = set(re.findall(r"[a-z0-9]+", text))
        for entry in self.list_faqs():
            if not entry["active"]:
                continue
            question = entry["question"].casefold()
            question_words = {
                word
                for word in re.findall(r"[a-z0-9]+", question)
                if word not in {"are", "can", "how", "i", "is", "the", "what", "you", "your"}
            }
            score = len(message_words & question_words)
            if question in text:
                score += len(question_words) + 1
            if score < 2:
                continue
            candidate = (score, entry)
            if matched is None or candidate[0] > matched[0]:
                matched = candidate
        if matched is None:
            return None
        entry = matched[1]
        answer = entry["answer"]
        if entry["title"].casefold() == "office hours":
            office_hours = self.get_settings().get("officeHours")
            if office_hours:
                answer = f"The SOC Guidance Office is open from {office_hours}."
        return FAQAnswer(response=answer, source_context=answer)

    def get_appointment_configuration(self) -> dict[str, Any] | None:
        persisted = self._load((APPOINTMENT_AVAILABILITY_KEY,))
        if APPOINTMENT_AVAILABILITY_KEY not in persisted:
            return None
        try:
            return normalize_appointment_availability(
                persisted[APPOINTMENT_AVAILABILITY_KEY],
                allow_legacy=True,
            )
        except ValueError:
            return None

    def get_student_booking_options(self) -> dict[str, Any]:
        configuration = self.get_appointment_configuration()
        if (
            configuration is None
            or configuration["appointmentCategories"] is None
            or configuration["consultationModes"] is None
        ):
            return {"state": "unconfigured", "bookingEnabled": False}
        return {
            "state": "available" if configuration["bookingEnabled"] else "unavailable",
            "bookingEnabled": configuration["bookingEnabled"],
            "officeAvailability": configuration["officeAvailability"],
            "unavailableDates": sorted(
                set(configuration["holidays"])
                | set(configuration["academicCalendarExclusions"])
                | set(configuration["unavailableDates"])
            ),
            "appointmentCategories": configuration["appointmentCategories"],
            "consultationModes": configuration["consultationModes"],
        }


settings_service = SettingsService()


__all__ = [
    "APPOINTMENT_AVAILABILITY_KEY",
    "FAQ_SETTING_KEY",
    "FAQAnswer",
    "SettingsService",
    "normalize_faq_entries",
    "normalize_appointment_availability",
    "settings_service",
]