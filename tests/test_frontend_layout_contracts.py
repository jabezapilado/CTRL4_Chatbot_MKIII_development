"""Lightweight contracts for the staff dashboard responsive-layout fixes."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class FrontendLayoutContractTests(unittest.TestCase):
    def test_notifications_mount_in_the_dashboard_header(self) -> None:
        template = _read("frontend/templates/dashboard.html")
        notifications = _read("frontend/static/js/notifications.js")
        stylesheet = _read("frontend/static/css/notifications.css")

        self.assertIn('data-notifications-mount', template)
        self.assertIn('const headerMount = document.querySelector("[data-notifications-mount]")', notifications)
        self.assertIn("notifications-widget--header", notifications)
        self.assertIn(".notifications-widget--header .notifications-panel", stylesheet)

    def test_manual_appointment_is_a_reachable_section_and_keeps_its_api(self) -> None:
        template = _read("frontend/templates/dashboard.html")
        dashboard = _read("frontend/static/js/dashboard.js")

        self.assertIn('id="manual-appointment-panel"', template)
        self.assertIn('data-dashboard-section="manual"', template)
        self.assertIn('data-dashboard-section-target="manual"', template)
        self.assertIn('`${API_BASE}/api/appointments/manual`', dashboard)
        self.assertIn('method: "POST"', dashboard)

    def test_section_navigation_is_responsive_and_uses_no_inline_handlers(self) -> None:
        template = _read("frontend/templates/dashboard.html")
        dashboard = _read("frontend/static/js/dashboard.js")
        stylesheet = _read("frontend/static/css/dashboard.css")

        self.assertIn('data-dashboard-section-nav="appointments"', template)
        self.assertIn('data-dashboard-section-nav="reports"', template)
        self.assertIn("function bindDashboardSectionNavigation()", dashboard)
        self.assertIn("function setSidebarOpen(open", dashboard)
        self.assertIn('event.key === "Escape"', dashboard)
        self.assertIn('aria-controls="sidebar"', template)
        self.assertIn('id="sidebar-close"', template)
        self.assertNotIn("onclick=", template)
        self.assertIn("@media (max-width: 900px)", stylesheet)
        self.assertIn("@media (max-width: 480px)", stylesheet)

    def test_no_obsolete_frontend_mutations_or_unsafe_manual_search_rendering(self) -> None:
        dashboard = _read("frontend/static/js/dashboard.js")

        self.assertNotIn("POST /api/inquiries", dashboard)
        self.assertNotIn("PATCH /api/conversation-summaries/", dashboard)
        self.assertIn("name.textContent = student.full_name", dashboard)
        self.assertNotIn("option.innerHTML", dashboard)
        self.assertIn("function appendTableEmptyState", dashboard)

    def test_chat_message_pane_keeps_footer_controls_in_the_flex_layout(self) -> None:
        template = _read("frontend/templates/chatbot.html")
        stylesheet = _read("frontend/static/css/chatbot.css")

        self.assertIn('id="chat-area"', template)
        self.assertIn('id="quick-replies"', template)
        self.assertIn('class="input-bar"', template)
        self.assertIn(".chat-area {\n  flex: 1;\n  min-height: 0;", stylesheet)
        self.assertIn(".quick-replies {\n  display: flex;", stylesheet)
        self.assertIn("height: 100dvh;", stylesheet)


if __name__ == "__main__":
    unittest.main()
