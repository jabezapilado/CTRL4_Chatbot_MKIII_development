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

    def test_inbox_uses_summary_projection_without_raw_chat_or_takeover_navigation(self) -> None:
        dashboard = _read("frontend/static/js/dashboard.js")
        template = _read("frontend/templates/dashboard.html")
        frontend_routes = _read("backend/server/routes/frontend_routes.py")

        self.assertIn("/api/staff/inbox", dashboard)
        self.assertIn("function inboxItemsForCurrentFilter", dashboard)
        self.assertIn("function openInboxItem", dashboard)
        self.assertNotIn("conversation_json", dashboard)
        self.assertNotIn("/api/inquiries", dashboard)
        self.assertNotIn("chatbot_admin", template)
        self.assertNotIn('"/chatbot_admin"', frontend_routes)
        self.assertNotIn("def chatbot_admin", frontend_routes)
        self.assertIn('id="inbox-search-input"', template)
        self.assertIn('id="inbox-filter"', template)

    def test_inbox_dashboard_uses_balanced_desktop_layout(self) -> None:
        template = _read("frontend/templates/dashboard.html")
        dashboard = _read("frontend/static/js/dashboard.js")
        stylesheet = _read("frontend/static/css/dashboard.css")

        self.assertIn("min-height: 100dvh", stylesheet)
        self.assertIn("height: 100dvh", stylesheet)
        self.assertIn('class="inbox-toolbar-controls"', template)
        self.assertIn('class="search-box inbox-search-box"', template)
        self.assertIn("max-height: clamp(260px, 36dvh, 460px);", stylesheet)
        self.assertIn(".inbox-table {", stylesheet)
        self.assertIn("table-layout: fixed;", stylesheet)
        self.assertIn(".inbox-table th:nth-child(4)", stylesheet)
        self.assertIn("width: 24%;", stylesheet)
        self.assertRegex(
            stylesheet,
            r"\.inbox-table th:nth-child\(6\),\s*"
            r"\.inbox-table td:nth-child\(6\) \{\s*width: 16%;",
        )
        self.assertRegex(
            stylesheet,
            r"\.inbox-table td:nth-child\(6\) \{[^}]*"
            r"overflow-wrap: anywhere;[^}]*white-space: normal;",
        )
        self.assertRegex(
            stylesheet,
            r"\.inbox-table th:nth-child\(7\),\s*"
            r"\.inbox-table td:nth-child\(7\) \{\s*"
            r"width: 7%;\s*overflow: hidden;",
        )
        self.assertIn("white-space: nowrap;", stylesheet)
        self.assertIn("padding-right: 22px;", stylesheet)
        self.assertIn("line-clamp: 2;", stylesheet)
        self.assertIn(".inbox-table thead th", stylesheet)
        self.assertIn("position: sticky;", stylesheet)
        self.assertIn('row.className = "inbox-record";', dashboard)
        self.assertIn('student.dataset.label = "Student";', dashboard)
        self.assertIn('preview.dataset.label = "Summary Preview";', dashboard)
        self.assertIn('action.dataset.label = "Action";', dashboard)
        self.assertRegex(
            stylesheet,
            r"@media \(max-width: 1279px\) \{\s*"
            r"#view-inbox \.table-wrap \{\s*max-height: none;",
        )
        self.assertIn("min-width: 0;\n    table-layout: auto;", stylesheet)
        self.assertIn("content: attr(data-label);", stylesheet)
        self.assertIn("grid-template-columns: 92px minmax(0, 1fr);", stylesheet)
        self.assertIn(".inbox-table .action-link", stylesheet)

    def test_mobile_sidebar_swaps_hamburger_for_existing_close_button(self) -> None:
        template = _read("frontend/templates/dashboard.html")
        dashboard = _read("frontend/static/js/dashboard.js")
        stylesheet = _read("frontend/static/css/dashboard.css")

        self.assertIn('id="sidebar-toggle"', template)
        self.assertIn('id="sidebar-close"', template)
        self.assertIn(
            'document.body.classList.toggle("sidebar-drawer-open", open);',
            dashboard,
        )
        self.assertIn("body.sidebar-drawer-open .sidebar-toggle", stylesheet)
        self.assertIn("width: min(280px, calc(100vw - 44px));", stylesheet)
        self.assertIn("flex: 0 0 44px;", stylesheet)

    def test_dashboard_header_and_stat_cards_keep_consistent_alignment(self) -> None:
        stylesheet = _read("frontend/static/css/dashboard.css")

        self.assertIn("padding: 12px 28px;", stylesheet)
        self.assertIn("grid-template-columns: repeat(4, minmax(190px, 1fr));", stylesheet)
        self.assertIn("grid-template-columns: repeat(2, minmax(220px, 1fr));", stylesheet)
        self.assertIn("grid-template-columns: minmax(0, 1fr);", stylesheet)
        self.assertIn("min-height: 100px;", stylesheet)
        self.assertIn("min-height: 32px;", stylesheet)
        self.assertIn("min-height: 40px;", stylesheet)

    def test_reports_page_uses_scoped_compact_analytics_layout(self) -> None:
        template = _read("frontend/templates/dashboard.html")
        stylesheet = _read("frontend/static/css/dashboard.css")

        self.assertIn('id="view-reports"', template)
        self.assertIn('id="reports-overview-kpis"', template)
        self.assertIn('data-dashboard-section-nav="reports"', template)
        self.assertIn("#view-reports #reports-overview-kpis", stylesheet)
        self.assertIn("#view-reports .dashboard-section-nav", stylesheet)
        self.assertIn("min-height: 34px;", stylesheet)
        self.assertIn("#view-reports .form-grid", stylesheet)
        self.assertIn(
            "grid-template-columns: repeat(2, minmax(170px, 220px)) minmax(260px, 1fr);",
            stylesheet,
        )
        self.assertIn('#view-reports .form-group input[type="date"]', stylesheet)
        self.assertIn("#view-reports .panel > .action-row", stylesheet)
        self.assertIn("#view-reports .inquiry-table", stylesheet)
        self.assertIn("table-layout: fixed;", stylesheet)
        self.assertIn("#view-reports .inquiry-table .table-empty-state", stylesheet)
        self.assertIn("#view-reports [data-dashboard-section] > .stat-grid", stylesheet)

    def test_settings_page_uses_scoped_compact_form_layout(self) -> None:
        template = _read("frontend/templates/dashboard.html")
        stylesheet = _read("frontend/static/css/dashboard.css")

        self.assertIn('id="view-settings"', template)
        self.assertIn('class="settings-panel appointment-settings-panel"', template)
        self.assertIn('class="settings-panel faq-management-panel"', template)
        self.assertIn('class="settings-panel counselor-profile-panel"', template)
        self.assertIn('class="settings-panel settings-password-panel"', template)
        self.assertIn('class="sub password-helper"', template)
        self.assertNotIn('id="student-password-panel"\n              style=', template)
        self.assertNotIn('id="change-password-btn"\n                style=', template)
        self.assertIn("#view-settings .settings-panel", stylesheet)
        self.assertIn("#view-settings .field-grid-2", stylesheet)
        self.assertIn("grid-template-columns: repeat(2, minmax(220px, 1fr));", stylesheet)
        self.assertIn("#view-settings .appointment-availability-window", stylesheet)
        self.assertIn("#view-settings .counselor-schedule-row", stylesheet)
        self.assertIn("#view-settings .faq-editor-card", stylesheet)
        self.assertIn("#view-settings .settings-password-panel", stylesheet)
        self.assertIn("#view-settings .password-helper", stylesheet)
        self.assertIn("box-shadow: 0 0 0 3px rgba(211, 84, 0, 0.12);", stylesheet)

    def test_staff_sidebar_uses_compact_aligned_flex_layout(self) -> None:
        template = _read("frontend/templates/dashboard.html")
        stylesheet = _read("frontend/static/css/dashboard.css")

        self.assertIn('class="sidebar"', template)
        self.assertIn("height: 100dvh;", stylesheet)
        self.assertIn("overflow-y: auto;", stylesheet)
        self.assertIn("margin-bottom: auto;", stylesheet)
        self.assertIn("min-height: 36px;", stylesheet)
        self.assertIn(".nav-item span:first-child", stylesheet)
        self.assertIn("min-width: 17px;", stylesheet)
        self.assertIn("height: 17px;", stylesheet)
        self.assertIn("#dashboard-logout", stylesheet)

    def test_case_details_layout_preserves_scoped_readable_cards(self) -> None:
        template = _read("frontend/templates/dashboard.html")
        stylesheet = _read("frontend/static/css/dashboard.css")

        self.assertIn('class="case-profile-identity"', template)
        self.assertIn('class="case-profile-heading"', template)
        self.assertIn("#view-case-details .case-layout", stylesheet)
        self.assertIn("grid-template-columns: minmax(0, 1fr) minmax(300px, 340px);", stylesheet)
        self.assertIn("#view-case-details .case-side-panel", stylesheet)
        self.assertIn("min-width: 300px;", stylesheet)
        self.assertIn("#view-case-details .case-message-box", stylesheet)
        self.assertIn("line-height: 1.58;", stylesheet)
        self.assertIn("#view-case-details .case-meta-cell", stylesheet)
        self.assertIn("min-height: 72px;", stylesheet)
        self.assertIn("#view-case-details .insight-row", stylesheet)
        self.assertIn("min-height: 42px;", stylesheet)
        self.assertIn("#view-case-details .case-confidentiality-card", stylesheet)
        self.assertIn("#view-case-details .staff-notes-card textarea", stylesheet)

    def test_flagged_cases_table_matches_compact_dashboard_layout(self) -> None:
        template = _read("frontend/templates/dashboard.html")
        dashboard = _read("frontend/static/js/dashboard.js")
        stylesheet = _read("frontend/static/css/dashboard.css")

        self.assertIn('class="panel flagged-panel"', template)
        self.assertIn('class="inquiry-table flagged-table"', template)
        self.assertIn("flagged-student-name", dashboard)
        self.assertIn("flagged-student-number", dashboard)
        self.assertIn("flagged-summary-preview", dashboard)
        self.assertIn("#view-flagged .flagged-panel > .sub", stylesheet)
        self.assertIn(".flagged-table {", stylesheet)
        self.assertIn("table-layout: fixed;", stylesheet)
        self.assertIn("min-width: 900px;", stylesheet)
        self.assertIn(".flagged-table th:nth-child(2)", stylesheet)
        self.assertIn("width: 42%;", stylesheet)
        self.assertIn(".flagged-summary-preview", stylesheet)
        self.assertIn("line-clamp: 2;", stylesheet)
        self.assertIn(".flagged-table .table-empty-state", stylesheet)

    def test_appointments_page_uses_compact_scoped_cards_and_details(self) -> None:
        template = _read("frontend/templates/dashboard.html")
        stylesheet = _read("frontend/static/css/dashboard.css")

        self.assertIn('class="stat-grid appointment-stat-grid"', template)
        self.assertIn('class="panel appointment-panel appointment-list-panel"', template)
        self.assertIn('class="search-box appointment-search-box"', template)
        self.assertIn("#view-appointments .appointment-panel > .sub", stylesheet)
        self.assertIn(".appointment-stat-grid", stylesheet)
        self.assertIn("grid-template-columns: repeat(3, minmax(190px, 1fr));", stylesheet)
        self.assertIn("#view-appointments .form-grid", stylesheet)
        self.assertIn(
            "grid-template-columns: repeat(2, minmax(170px, 220px)) minmax(240px, 1fr);",
            stylesheet,
        )
        self.assertIn('#view-appointments .form-group input[type="date"]', stylesheet)
        self.assertIn("#view-appointments .appointment-card-footer .btn", stylesheet)
        self.assertIn(".appointment-meta-grid", stylesheet)
        self.assertIn("grid-template-columns: repeat(4, minmax(120px, 1fr));", stylesheet)
        self.assertIn("#view-appointment-details .case-layout", stylesheet)
        self.assertIn("grid-template-columns: minmax(0, 1fr) minmax(300px, 340px);", stylesheet)
        self.assertIn("#view-appointment-details .staff-notes-card textarea", stylesheet)

    def test_phone_tablet_desktop_responsive_guardrails_are_present(self) -> None:
        dashboard = _read("frontend/static/css/dashboard.css")
        appointment = _read("frontend/static/css/appointment.css")
        case_status = _read("frontend/static/css/case_status.css")
        chatbot = _read("frontend/static/css/chatbot.css")
        admin = _read("frontend/static/css/admin.css")

        self.assertIn("@media (max-width: 700px)", dashboard)
        self.assertIn(".dash-main {\n    overflow-x: clip;", dashboard)
        self.assertIn("#view-appointment-details .case-side-panel", dashboard)
        self.assertIn("grid-template-columns: minmax(0, 1fr);", dashboard)
        self.assertIn("#view-appointments .appointment-card-footer .btn", dashboard)

        self.assertIn("overflow-x: hidden;", appointment)
        self.assertIn("min-height: 100dvh;", appointment)
        self.assertIn("@media (max-width: 960px) and (orientation: landscape)", appointment)
        self.assertIn("max-height: calc(100dvh - 32px);", appointment)

        self.assertIn("overflow-x: hidden;", case_status)
        self.assertIn("min-height: 100dvh;", case_status)
        self.assertIn("flex-direction: column;", case_status)
        self.assertIn("@media (max-width: 900px) and (orientation: landscape)", case_status)

        self.assertIn("min-width: 0;", chatbot)
        self.assertIn("@media (max-width: 900px) and (orientation: landscape)", chatbot)
        self.assertIn("max-width: 100vw;", chatbot)

        self.assertIn("max-height: min(90dvh, 900px);", admin)
        self.assertIn(".program-catalog-row {\n    grid-template-columns: 1fr;", admin)
        self.assertIn("@media (max-width: 900px) and (orientation: landscape)", admin)

    def test_case_staff_actions_match_routine_or_flagged_status(self) -> None:
        dashboard = _read("frontend/static/js/dashboard.js")
        template = _read("frontend/templates/dashboard.html")

        self.assertIn('id="case-staff-actions-note"', template)
        self.assertIn("No immediate intervention is required.", dashboard)
        self.assertIn(
            "Immediate Guidance Office review is recommended.",
            dashboard,
        )
        chat = _read("frontend/static/js/chat.js")
        self.assertIn("For your safety, your conversation has been referred", chat)

    def test_case_details_separates_persisted_emotion_from_safety_risk(self) -> None:
        dashboard = _read("frontend/static/js/dashboard.js")
        template = _read("frontend/templates/dashboard.html")

        self.assertIn("function displayCaseEmotion(detail)", dashboard)
        self.assertIn("function safetyRiskPresentation(detail)", dashboard)
        self.assertIn("function applySafetyRisk(detail)", dashboard)
        self.assertIn('return capitalize(detail.emotion_results || "Unavailable");', dashboard)
        self.assertIn('id="case-safety-risk"', template)
        self.assertIn("No immediate safety concern", dashboard)
        self.assertIn("Elevated concern", dashboard)
        self.assertIn("Immediate safety concern", dashboard)
        self.assertIn("safety escalation|crisis|self[ -]?harm|suicid|high-risk", dashboard)

    def test_appointment_times_are_controlled_selects_with_touched_validation(self) -> None:
        template = _read("frontend/templates/appointment.html")
        appointment = _read("frontend/static/js/appointment.js")
        dashboard = _read("frontend/static/js/dashboard.js")

        self.assertIn('<select\n                  id="prefTime"'.replace("\\n", "\n"), template)
        self.assertIn('<select\n                id="rescheduleTime"'.replace("\\n", "\n"), template)
        self.assertNotIn('type="text"\n                  id="prefTime"'.replace("\\n", "\n"), template)
        self.assertIn("function populateSlotSelect", appointment)
        self.assertIn("function loadSlotOptions", appointment)
        self.assertIn("const touchedFields = new Set()", appointment)
        self.assertIn("Select an available time slot", appointment)
        self.assertIn("No available time slots for the selected date.", appointment)
        self.assertIn('<select id="manual-appointment-time" disabled>', dashboard)
        self.assertIn("function populateManualSlotSelect", dashboard)

    def test_manual_autocomplete_and_counselor_profile_use_safe_controls(self) -> None:
        dashboard = _read("frontend/static/js/dashboard.js")
        template = _read("frontend/templates/dashboard.html")

        self.assertIn("Search by name, student number, or email", dashboard)
        self.assertIn("manual-student-search-results", dashboard)
        self.assertIn("studentSearchResults.addEventListener(\"keydown\"", dashboard)
        self.assertIn("student_number: selectedStudent.student_number", dashboard)
        self.assertNotIn("account_id: selectedStudent.id", dashboard)
        self.assertIn("My Counselor Profile", template)
        self.assertIn("counselor-profile-rooms", template)
        self.assertIn("counselor-schedule-list", template)

    def test_chat_message_pane_keeps_footer_controls_in_the_flex_layout(self) -> None:
        template = _read("frontend/templates/chatbot.html")
        chat = _read("frontend/static/js/chat.js")
        stylesheet = _read("frontend/static/css/chatbot.css")

        self.assertIn('id="chat-area"', template)
        self.assertIn('id="quick-replies"', template)
        self.assertIn('class="input-bar"', template)
        self.assertIn(".chat-area {\n  flex: 1;\n  min-height: 0;", stylesheet)
        self.assertIn(".quick-replies {\n  display: flex;", stylesheet)
        self.assertIn("height: 100dvh;", stylesheet)
        self.assertIn("data-quick-message", template)
        self.assertNotIn("qrBar.style.display", chat)
        self.assertIn('id="active-chat-state"', template)
        self.assertIn('document.getElementById("active-chat-state")', chat)
        self.assertIn("restoreVisibleChat(activeChat)", chat)
        self.assertNotIn("localStorage.setItem", chat)
        self.assertNotIn("sessionStorage.setItem", chat)
        self.assertIn('transient_chat_service.clear(getattr(session, "sid", ""), user.get("id"))', _read("backend/server/auth.py"))
        self.assertIn('response.headers["Cache-Control"] = "no-store"', _read("backend/server/routes/frontend_routes.py"))


if __name__ == "__main__":
    unittest.main()
