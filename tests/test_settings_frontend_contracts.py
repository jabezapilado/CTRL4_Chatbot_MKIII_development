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
        self.assertIn('title: "Guidance Office Settings"', dashboard)
        self.assertNotIn("Chatbot / FAQ Settings", template)
        self.assertNotIn("Escalation Settings", template)
        self.assertIn("Office Information", template)
        self.assertIn("Appointment Availability", template)
        self.assertIn("Account Security", template)
        self.assertNotIn("onclick=", template)

    def test_availability_rows_have_distinct_controls_and_canonical_payloads(self) -> None:
        dashboard = _read("frontend/static/js/dashboard.js")

        self.assertIn('weekday.dataset.availabilityWeekday = "true"', dashboard)
        self.assertIn('startTime.type = "time"', dashboard)
        self.assertIn('endTime.type = "time"', dashboard)
        self.assertIn("inputTimeToCanonical", dashboard)
        self.assertIn('time: `${canonicalStartTime} - ${canonicalEndTime}`', dashboard)
        self.assertIn("Correct the highlighted availability rows before saving.", dashboard)

    def test_availability_panel_is_full_width_and_responsive(self) -> None:
        template = _read("frontend/templates/dashboard.html")
        stylesheet = _read("frontend/static/css/dashboard.css")

        self.assertIn('class="settings-panel appointment-settings-panel"', template)
        self.assertIn("grid-template-columns: 1fr;", stylesheet)
        self.assertIn(".appointment-availability-window {", stylesheet)
        self.assertIn("grid-template-columns: 1fr;", stylesheet)


if __name__ == "__main__":
    unittest.main()