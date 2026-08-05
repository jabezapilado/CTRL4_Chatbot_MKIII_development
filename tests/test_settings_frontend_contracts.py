from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class SettingsFrontendContractTests(unittest.TestCase):
    def test_settings_are_persisted_not_browser_local(self) -> None:
        dashboard = _read("frontend/static/js/dashboard.js")

        self.assertIn("loadPersistedSettings", dashboard)
        self.assertIn("saveSettingsToApi", dashboard)
        self.assertNotIn("localStorage", dashboard)
        self.assertNotIn("defaultSettings", dashboard)

    def test_appointment_forms_use_the_shared_booking_projection(self) -> None:
        dashboard = _read("frontend/static/js/dashboard.js")
        appointment = _read("frontend/static/js/appointment.js")
        template = _read("frontend/templates/appointment.html")

        self.assertIn("/api/appointments/booking-options", dashboard)
        self.assertIn("/api/appointments/booking-options", appointment)
        self.assertIn("refreshAppointmentBookingOptions", dashboard)
        self.assertIn("refreshBookingOptions", appointment)
        self.assertNotIn('option value="08:00 AM"', template)
        self.assertNotIn('option value="home_family"', template)

    def test_disconnected_controls_are_not_presented_as_operational(self) -> None:
        dashboard = _read("frontend/static/js/dashboard.js")
        template = _read("frontend/templates/dashboard.html")

        self.assertNotIn("addFaqFromButton", dashboard)
        self.assertNotIn("autoFlag", dashboard)
        self.assertNotIn("showSupport", dashboard)
        self.assertIn("not staff-configurable", template)
        self.assertNotIn("onclick=", template)


if __name__ == "__main__":
    unittest.main()