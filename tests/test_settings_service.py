from __future__ import annotations

import unittest
from flask import Flask
from pathlib import Path
from unittest.mock import patch

from backend.server.services.settings_service import SettingsService


def configured_availability() -> dict:
    return {
        "bookingEnabled": True,
        "officeAvailability": [
            {"days": "monday-friday", "time": "9:00 am - 5:00 pm"},
        ],
        "holidays": ["2026-12-25"],
        "academicCalendarExclusions": [],
        "unavailableDates": ["2026-11-01"],
        "appointmentCategories": ["Academic", "Personal"],
        "consultationModes": ["onsite", "online"],
    }


class SettingsServiceTests(unittest.TestCase):
    def test_update_normalizes_and_persists_supported_settings(self) -> None:
        saved: list[dict] = []
        service = SettingsService(load=lambda _keys: {}, save=saved.append)

        service.update_settings(
            {
                "officeHours": " Monday to Friday, 9:00 AM - 5:00 PM ",
                "appointmentAvailability": configured_availability(),
            }
        )

        self.assertEqual(saved[0]["officeHours"], "Monday to Friday, 9:00 AM - 5:00 PM")
        availability = saved[0]["appointmentAvailability"]
        self.assertEqual(availability["officeAvailability"][0]["days"], "Monday to Friday")
        self.assertEqual(availability["officeAvailability"][0]["time"], "09:00 AM - 05:00 PM")

    def test_invalid_availability_fails_without_persisting(self) -> None:
        saved: list[dict] = []
        service = SettingsService(load=lambda _keys: {}, save=saved.append)
        invalid = configured_availability()
        invalid["unavailableDates"] = ["not-a-date"]

        with self.assertRaisesRegex(ValueError, "Unavailable dates"):
            service.update_settings({"appointmentAvailability": invalid})

        self.assertEqual(saved, [])

    def test_student_projection_excludes_internal_configuration(self) -> None:
        service = SettingsService(
            load=lambda _keys: {"appointmentAvailability": configured_availability()}
        )

        options = service.get_student_booking_options()

        self.assertEqual(options["state"], "available")
        self.assertNotIn("holidays", options)
        self.assertNotIn("academicCalendarExclusions", options)
        self.assertNotIn("staff_id", options)

    def test_missing_configuration_is_explicitly_unconfigured(self) -> None:
        service = SettingsService(load=lambda _keys: {})

        self.assertEqual(
            service.get_student_booking_options(),
            {"state": "unconfigured", "bookingEnabled": False},
        )

    def test_staff_configuration_disables_booking_without_losing_structure(self) -> None:
        availability = configured_availability()
        availability["bookingEnabled"] = False
        service = SettingsService(
            load=lambda _keys: {"appointmentAvailability": availability}
        )

        options = service.get_student_booking_options()

        self.assertEqual(options["state"], "unavailable")
        self.assertFalse(options["bookingEnabled"])
        self.assertIn("officeAvailability", options)


class SettingsRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        from backend.server.routes.appointment_routes import appointment_bp
        from backend.server.routes.settings_routes import settings_bp

        self.app = Flask(__name__)
        self.app.secret_key = "test-settings-routes"
        self.app.register_blueprint(settings_bp)
        self.app.register_blueprint(appointment_bp)

    def _client_for(self, role: str):
        client = self.app.test_client()
        with client.session_transaction() as session:
            session["hau_user"] = {
                "id": 1,
                "email": f"{role}@example.test",
                "role": role,
            }
        return client

    def test_settings_route_delegates_to_service_and_rejects_student_access(self) -> None:
        from backend.server.routes import settings_routes

        with patch.object(
            settings_routes.settings_service,
            "get_settings",
            return_value={"appointmentConfigurationState": "unconfigured"},
        ) as get_settings:
            response = self._client_for("staff").get("/api/settings")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])
        get_settings.assert_called_once_with()
        self.assertEqual(self._client_for("student").get("/api/settings").status_code, 403)

    def test_booking_options_are_shared_and_student_safe(self) -> None:
        from backend.server.routes import appointment_routes

        options = {
            "state": "available",
            "bookingEnabled": True,
            "officeAvailability": [{"days": "Monday", "time": "09:00 AM - 05:00 PM"}],
        }
        with patch.object(
            appointment_routes.settings_service,
            "get_student_booking_options",
            return_value=options,
        ):
            response = self._client_for("student").get("/api/appointments/booking-options")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"], options)
        self.assertNotIn("staff_id", response.get_json()["data"])

    def test_invalid_settings_are_reported_with_the_standard_error_envelope(self) -> None:
        from backend.server.routes import settings_routes

        with patch.object(
            settings_routes.settings_service,
            "update_settings",
            side_effect=ValueError("Appointment availability is invalid."),
        ):
            response = self._client_for("staff").post("/api/settings", json={})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {
                "success": False,
                "message": "Appointment availability is invalid.",
                "errors": None,
            },
        )

    def test_settings_route_has_no_direct_database_dependency(self) -> None:
        route_source = (
            Path(__file__).resolve().parents[1]
            / "backend/server/routes/settings_routes.py"
        ).read_text(encoding="utf-8")

        self.assertIn("settings_service", route_source)
        self.assertNotIn("from ..db", route_source)


class AppointmentSettingsIntegrationTests(unittest.TestCase):
    def test_configured_category_and_mode_are_authoritative(self) -> None:
        from backend.server.services import appointment_service

        counselor = {
            "consultation_rooms": '["Room 1"]',
            "consultation_schedules": (
                '[{"room":"Room 1","days":"Monday to Friday",'
                '"time":"09:00 AM - 05:00 PM"}]'
            ),
        }
        configuration = configured_availability()
        with patch.object(
            appointment_service.settings_service,
            "get_appointment_configuration",
            return_value=configuration,
        ):
            appointment_service._validate_booking_constraints(
                counselor,
                "2026-08-10",
                "09:00 AM",
                "Academic",
                "onsite",
            )
            with self.assertRaisesRegex(ValueError, "appointment category"):
                appointment_service._validate_booking_constraints(
                    counselor,
                    "2026-08-10",
                    "09:00 AM",
                    "Removed category",
                    "onsite",
                )

    def test_operational_answers_read_the_settings_service(self) -> None:
        from backend.server.services.operational_guidance_service import (
            OperationalGuidanceService,
        )
        from backend.server.services.settings_service import settings_service

        with patch.object(
            settings_service,
            "get_settings",
            return_value={"officeHours": "Weekdays, 9:00 AM - 5:00 PM"},
        ):
            answer = OperationalGuidanceService().answer(
                "What are your office hours?",
                {"id": 1, "role": "student"},
            )

        self.assertIsNotNone(answer)
        self.assertIn("Weekdays, 9:00 AM - 5:00 PM", answer.response)