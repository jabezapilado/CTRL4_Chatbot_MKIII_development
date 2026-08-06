from __future__ import annotations

import unittest
from flask import Flask
from pathlib import Path
from unittest.mock import patch

from backend.server.services.settings_service import (
    APPROVED_APPOINTMENT_AVAILABILITY,
    FAQ_SETTING_KEY,
    SettingsService,
    normalize_appointment_availability,
)


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
    @staticmethod
    def _memory_service(initial: dict | None = None) -> tuple[SettingsService, dict, list[dict]]:
        store = dict(initial or {})
        writes: list[dict] = []

        def load(keys):  # type: ignore[no-untyped-def]
            return {key: store[key] for key in keys if key in store}

        def save(updates):  # type: ignore[no-untyped-def]
            writes.append(dict(updates))
            store.update(updates)

        return SettingsService(load=load, save=save), store, writes

    def test_clean_installation_seeds_approved_mk_ii_values(self) -> None:
        service, store, _writes = self._memory_service()

        report = service.seed_approved_mk_ii_settings()

        self.assertIn("officeName", report["seeded"])
        self.assertEqual(store["officeName"], "SOC Guidance Office")
        self.assertEqual(store["officeHours"], "Monday to Friday, 7:00 AM to 5:00 PM")
        self.assertEqual(store["contactNumber"], "")
        availability = store["appointmentAvailability"]
        self.assertTrue(availability["bookingEnabled"])
        self.assertEqual(len(availability["officeAvailability"]), 5)
        self.assertNotIn(
            "Sunday",
            [window["days"] for window in availability["officeAvailability"]],
        )
        self.assertEqual(
            availability["appointmentCategories"],
            APPROVED_APPOINTMENT_AVAILABILITY["appointmentCategories"],
        )
        self.assertEqual(
            availability["consultationModes"],
            ["Online", "Onsite"],
        )
        self.assertEqual(len(store[FAQ_SETTING_KEY]), 3)
        options = service.get_student_booking_options()
        self.assertEqual(options["appointmentCategories"], availability["appointmentCategories"])
        self.assertEqual(options["consultationModes"], availability["consultationModes"])

    def test_seed_preserves_staff_edits_and_is_idempotent(self) -> None:
        edited_availability = configured_availability()
        edited_availability["appointmentSlots"] = ["09:00 AM"]
        edited = {
            "officeHours": "Staff edited hours",
            "contactNumber": "",
            "appointmentAvailability": edited_availability,
            FAQ_SETTING_KEY: [
                {
                    "id": "staff-faq",
                    "title": "Staff FAQ",
                    "question": "What changed?",
                    "answer": "Staff authored answer.",
                    "active": True,
                    "order": 1,
                }
            ],
        }
        service, store, writes = self._memory_service(edited)

        first_report = service.seed_approved_mk_ii_settings()
        second_report = service.seed_approved_mk_ii_settings()

        self.assertEqual(store["officeHours"], "Staff edited hours")
        self.assertEqual(store[FAQ_SETTING_KEY][0]["id"], "staff-faq")
        self.assertIn("appointmentAvailability", first_report["preserved"])
        self.assertEqual(second_report["seeded"], [])
        self.assertEqual(len(writes), 1)

    def test_seed_adds_missing_slots_without_replacing_existing_configuration(self) -> None:
        availability = configured_availability()
        service, store, _writes = self._memory_service(
            {"appointmentAvailability": availability}
        )

        service.seed_approved_mk_ii_settings()

        seeded = store["appointmentAvailability"]
        self.assertEqual(seeded["officeAvailability"], availability["officeAvailability"])
        self.assertEqual(seeded["appointmentCategories"], availability["appointmentCategories"])
        self.assertIn("appointmentSlots", seeded)

    def test_seed_leaves_documented_counselor_rooms_profile_owned(self) -> None:
        staff_profile = {
            "consultation_rooms": ["SJH-206", "PGN-105"],
            "consultation_schedules": [
                {"room": "SJH-206", "days": "Monday to Friday", "time": "08:00 AM - 05:00 PM"}
            ],
        }
        service, store, _writes = self._memory_service({"staff-profile": staff_profile})

        service.seed_approved_mk_ii_settings()

        self.assertEqual(store["staff-profile"], staff_profile)
        self.assertNotIn("PGN-105", store["officeLocation"])
        self.assertNotIn("PGN-109", store["officeLocation"])

    def test_faq_crud_persists_and_ignores_inactive_entries(self) -> None:
        service, store, _writes = self._memory_service()
        service.seed_approved_mk_ii_settings()

        created = service.create_faq(
            {
                "title": "Custom FAQ",
                "question": "Where is the custom office?",
                "answer": "The custom answer.",
            }
        )
        updated = service.update_faq(created["id"], {"active": False})

        self.assertFalse(updated["active"])
        self.assertEqual(len(service.list_faqs()), 4)
        self.assertIsNone(
            service.answer_faq(
                "Where is the custom office?",
                {"id": 1, "role": "student"},
            )
        )
        service.remove_faq(created["id"])
        self.assertEqual(len(store[FAQ_SETTING_KEY]), 3)

    def test_office_hours_faq_uses_current_runtime_setting(self) -> None:
        service, store, _writes = self._memory_service()
        service.seed_approved_mk_ii_settings()
        store["officeHours"] = "Monday to Friday, 8:00 AM to 4:00 PM"

        answer = service.answer_faq(
            "What are your office hours?",
            {"id": 1, "role": "student"},
        )

        self.assertIsNotNone(answer)
        self.assertIn("8:00 AM to 4:00 PM", answer.response)

    def test_counseling_services_faq_answers_speaking_with_a_counselor(self) -> None:
        service, _store, _writes = self._memory_service()
        service.seed_approved_mk_ii_settings()

        answer = service.answer_faq(
            "Can I speak with a counselor?",
            {"id": 1, "role": "student"},
        )

        self.assertIsNotNone(answer)
        self.assertIn("request counseling assistance", answer.response)
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

    def test_booking_disabled_allows_incomplete_configuration_but_blocks_booking(self) -> None:
        saved: list[dict] = []
        availability = configured_availability()
        availability.update(
            {
                "bookingEnabled": False,
                "officeAvailability": [],
                "appointmentCategories": [],
                "consultationModes": [],
            }
        )
        service = SettingsService(load=lambda _keys: {}, save=saved.append)

        service.update_settings({"appointmentAvailability": availability})

        self.assertEqual(saved[0]["appointmentAvailability"]["officeAvailability"], [])
        options = SettingsService(
            load=lambda _keys: saved[0]
        ).get_student_booking_options()
        self.assertEqual(options["state"], "unavailable")
        self.assertFalse(options["bookingEnabled"])
        self.assertEqual(
            SettingsService(
                load=lambda _keys: saved[0]
            ).get_settings()["appointmentConfigurationState"],
            "booking_disabled",
        )

    def test_booking_enabled_requires_windows_categories_and_modes(self) -> None:
        service = SettingsService(load=lambda _keys: {}, save=lambda _settings: None)

        for field_name, message in (
            ("officeAvailability", "Office availability must contain"),
            ("appointmentCategories", "Appointment categories must contain"),
            ("consultationModes", "Consultation modes must contain"),
        ):
            with self.subTest(field_name=field_name):
                availability = configured_availability()
                availability[field_name] = []
                with self.assertRaisesRegex(ValueError, message):
                    service.update_settings({"appointmentAvailability": availability})

    def test_complete_browser_window_payload_normalizes_and_round_trips(self) -> None:
        saved: list[dict] = []
        availability = configured_availability()
        availability["officeAvailability"] = [
            {"days": "Monday", "time": "07:00 AM - 09:00 AM"},
            {"days": "Sunday", "time": "09:00 AM - 05:00 PM"},
        ]
        service = SettingsService(load=lambda _keys: {}, save=saved.append)

        service.update_settings({"appointmentAvailability": availability})

        persisted = saved[0]["appointmentAvailability"]
        self.assertEqual(
            persisted["officeAvailability"],
            [
                {"days": "Monday", "time": "07:00 AM - 09:00 AM"},
                {"days": "Sunday", "time": "09:00 AM - 05:00 PM"},
            ],
        )

    def test_slot_configuration_normalizes_and_is_projected(self) -> None:
        saved: list[dict] = []
        availability = configured_availability()
        availability["appointmentSlots"] = ["3:00 pm", "9:00 am"]
        service = SettingsService(load=lambda _keys: {}, save=saved.append)

        service.update_settings({"appointmentAvailability": availability})

        slots = saved[0]["appointmentAvailability"]["appointmentSlots"]
        self.assertEqual(slots, ["09:00 AM", "03:00 PM"])

    def test_legacy_availability_values_normalize_for_current_controls(self) -> None:
        legacy = {
            "officeAvailability": [
                {"days": "monday-friday", "time": "7:00 am - 5:00 pm"}
            ],
            "holidays": [],
            "academicCalendarExclusions": [],
            "unavailableDates": [],
        }

        normalized = normalize_appointment_availability(legacy, allow_legacy=True)

        self.assertEqual(
            normalized["officeAvailability"],
            [{"days": "Monday to Friday", "time": "07:00 AM - 05:00 PM"}],
        )
        self.assertTrue(normalized["bookingEnabled"])

    def test_incomplete_or_reversed_window_is_rejected(self) -> None:
        service = SettingsService(load=lambda _keys: {}, save=lambda _settings: None)
        incomplete = configured_availability()
        incomplete["officeAvailability"] = [{"days": "Monday", "time": ""}]
        reversed_window = configured_availability()
        reversed_window["officeAvailability"] = [
            {"days": "Monday", "time": "09:00 AM - 07:00 AM"}
        ]

        with self.assertRaisesRegex(ValueError, "Availability time"):
            service.update_settings({"appointmentAvailability": incomplete})
        with self.assertRaisesRegex(ValueError, "end time must be after"):
            service.update_settings({"appointmentAvailability": reversed_window})


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
            "availableSlots": [],
        }
        with patch.object(
            appointment_routes,
            "get_booking_options_service",
            return_value=options,
        ) as get_options:
            response = self._client_for("student").get("/api/appointments/booking-options")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"], options)
        self.assertNotIn("staff_id", response.get_json()["data"])
        get_options.assert_called_once_with(
            {
                "id": 1,
                "email": "student@example.test",
                "role": "student",
            },
            preferred_date=None,
            student_number=None,
        )

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

    def test_faq_routes_delegate_to_service_and_keep_staff_rbac(self) -> None:
        from backend.server.routes import settings_routes

        entry = {
            "id": "faq-1",
            "title": "Office Hours",
            "question": "What are your office hours?",
            "answer": "Current hours.",
            "active": True,
            "order": 1,
        }
        with patch.object(settings_routes.settings_service, "list_faqs", return_value=[entry]), patch.object(
            settings_routes.settings_service, "create_faq", return_value=entry
        ), patch.object(settings_routes.settings_service, "update_faq", return_value=entry), patch.object(
            settings_routes.settings_service, "remove_faq"
        ) as remove_faq:
            self.assertEqual(self._client_for("staff").get("/api/settings/faqs").status_code, 200)
            self.assertEqual(
                self._client_for("staff").post("/api/settings/faqs", json=entry).status_code,
                201,
            )
            self.assertEqual(
                self._client_for("staff").patch("/api/settings/faqs/faq-1", json={"active": False}).status_code,
                200,
            )
            self.assertEqual(self._client_for("staff").delete("/api/settings/faqs/faq-1").status_code, 200)
            remove_faq.assert_called_once_with("faq-1")
        self.assertEqual(self._client_for("student").get("/api/settings/faqs").status_code, 403)


class AppointmentSettingsIntegrationTests(unittest.TestCase):
    def test_date_specific_slots_use_general_counselor_and_conflict_rules(self) -> None:
        from backend.server.services import appointment_service

        configuration = configured_availability()
        configuration["appointmentSlots"] = ["09:00 AM", "10:00 AM"]
        counselor = {
            "id": 8,
            "consultation_rooms": '["Room 1"]',
            "consultation_schedules": '[{"room":"Room 1","days":"Monday","time":"09:00 AM - 10:00 AM"}]',
        }
        student = {"id": 7, "program": "BSCS"}
        with patch.object(
            appointment_service.settings_service,
            "get_student_booking_options",
            return_value={
                "state": "available",
                "bookingEnabled": True,
                "officeAvailability": configuration["officeAvailability"],
                "unavailableDates": [],
                "appointmentCategories": configuration["appointmentCategories"],
                "consultationModes": configuration["consultationModes"],
                "appointmentSlots": configuration["appointmentSlots"],
            },
        ), patch.object(
            appointment_service.settings_service,
            "get_appointment_configuration",
            return_value=configuration,
        ), patch.object(
            appointment_service,
            "get_student_by_id",
            return_value=student,
        ), patch.object(
            appointment_service,
            "get_staff_by_program",
            return_value=counselor,
        ), patch.object(
            appointment_service,
            "list_appointments_by_date",
            return_value=[],
        ):
            options = appointment_service.get_booking_options_service(
                {"id": 7, "role": "student"},
                preferred_date="2026-08-10",
            )

        self.assertEqual(options["availableSlots"], ["09:00 AM"])

    def test_manipulated_slot_is_rejected_by_appointment_service(self) -> None:
        from backend.server.services import appointment_service

        counselor = {
            "consultation_rooms": '["Room 1"]',
            "consultation_schedules": '[{"room":"Room 1","days":"Monday","time":"09:00 AM - 05:00 PM"}]',
        }
        configuration = configured_availability()
        configuration["appointmentSlots"] = ["09:00 AM"]
        with patch.object(
            appointment_service.settings_service,
            "get_appointment_configuration",
            return_value=configuration,
        ), self.assertRaisesRegex(ValueError, "appointment time"):
            appointment_service._validate_booking_constraints(
                counselor,
                "2026-08-10",
                "10:00 AM",
                "Academic",
                "onsite",
            )
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

    def test_general_availability_and_counselor_schedule_are_separate_gates(self) -> None:
        from backend.server.services import appointment_service

        counselor = {
            "consultation_rooms": '["Room 1"]',
            "consultation_schedules": (
                '[{"room":"Room 1","days":"Monday",'
                '"time":"09:00 AM - 05:00 PM"}]'
            ),
        }
        configuration = configured_availability()
        configuration["officeAvailability"] = [
            {"days": "Sunday", "time": "09:00 AM - 05:00 PM"}
        ]
        with patch.object(
            appointment_service.settings_service,
            "get_appointment_configuration",
            return_value=configuration,
        ):
            with self.assertRaisesRegex(ValueError, "counselor's consultation schedule"):
                appointment_service._validate_booking_constraints(
                    counselor,
                    "2026-08-09",
                    "09:00 AM",
                    "Academic",
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