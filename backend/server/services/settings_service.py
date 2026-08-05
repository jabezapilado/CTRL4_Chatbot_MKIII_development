"""Validated, persisted application settings and appointment projections."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from typing import Any, Callable, Final

from ..db import load_persisted_settings


OFFICE_SETTING_KEYS: Final[tuple[str, ...]] = (
    "officeHours",
    "officeEmail",
    "contactNumber",
    "officeLocation",
)
APPOINTMENT_AVAILABILITY_KEY: Final[str] = "appointmentAvailability"
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
    "SettingsService",
    "normalize_appointment_availability",
    "settings_service",
]