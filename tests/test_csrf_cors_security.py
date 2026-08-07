"""Focused application-level CSRF and same-origin CORS regression coverage."""

from __future__ import annotations

import os
import re
import tempfile
import unittest
from unittest.mock import patch


class CsrfCorsSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        environment = {
            "CHATBOT_SESSION_TYPE": "cachelib",
            "CHATBOT_SESSION_FILE_DIR": self._temporary_directory.name,
            "CHATBOT_DATABASE_INITIALIZE_ON_START": "false",
        }
        self._environment = patch.dict(os.environ, environment, clear=False)
        self._environment.start()

        from backend.server import create_app

        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self._environment.stop()
        self._temporary_directory.cleanup()

    def _authenticate(self, role: str = "student", account_id: int = 1) -> None:
        with self.client.session_transaction() as browser_session:
            browser_session["hau_user"] = {
                "id": account_id,
                "email": f"{role}{account_id}@example.test",
                "role": role,
            }
            browser_session["_csrf_token"] = "test-csrf-token"

    def _csrf_headers(self) -> dict[str, str]:
        return {"X-CSRF-Token": "test-csrf-token"}

    def test_unsafe_authenticated_mutations_require_a_token(self) -> None:
        self._authenticate("staff")

        for method, path in (
            ("post", "/chat"),
            ("patch", "/api/notifications/7/read"),
            ("delete", "/api/settings/faqs/faq-7"),
        ):
            with self.subTest(method=method, path=path):
                response = getattr(self.client, method)(path, json={})
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response.get_json(), {
                    "success": False,
                    "message": "CSRF validation failed.",
                    "errors": None,
                })

    def test_login_bootstrap_and_logout_use_rotated_csrf_tokens(self) -> None:
        from backend.server import auth

        response = self.client.get("/login")
        match = re.search(rb'<meta name="csrf-token" content="([^"]+)"', response.data)
        self.assertIsNotNone(match)
        bootstrap_token = match.group(1).decode()  # type: ignore[union-attr]

        user = {"id": 9, "email": "student9@example.test", "role": "student"}
        with patch.object(auth, "login_service", return_value=user):
            login = self.client.post(
                "/auth/login",
                json={"email": user["email"], "password": "not-persisted"},
                headers={"X-CSRF-Token": bootstrap_token},
            )

        self.assertEqual(login.status_code, 200)
        with self.client.session_transaction() as browser_session:
            authenticated_token = browser_session["_csrf_token"]
        self.assertNotEqual(authenticated_token, bootstrap_token)

        logout = self.client.post(
            "/auth/logout",
            headers={"X-CSRF-Token": authenticated_token},
        )
        self.assertEqual(logout.status_code, 200)
        self.assertTrue(logout.get_json()["success"])

    def test_valid_csrf_tokens_preserve_student_staff_and_admin_mutations(self) -> None:
        from backend.server.routes import account_routes, appointment_routes, conversation_routes, settings_routes

        self._authenticate("student")
        booking = {
            "contact_number": "09171234567",
            "appointment_category": "Academic",
            "appointment_mode": "in_person",
            "preferred_date": "2026-08-08",
            "preferred_time_slot": "10:00 AM",
            "reason": "CSRF regression booking",
        }
        with patch.object(appointment_routes, "create_student_appointment", return_value=31):
            self.assertEqual(
                self.client.post(
                    "/api/appointments", json=booking, headers=self._csrf_headers()
                ).status_code,
                201,
            )

        self._authenticate("staff", 2)
        inbox_item = {"id": 45, "flagged_status": "flagged"}
        with patch.object(conversation_routes, "get_staff_inbox_item", return_value=inbox_item), patch.object(
            conversation_routes, "mark_staff_flagged_conversation_reviewed", return_value=inbox_item
        ), patch.object(
            conversation_routes, "create_staff_case_note", return_value={"id": 2, "note_text": "Checked"}
        ), patch.object(
            conversation_routes, "update_staff_case_confidentiality", return_value={"status": "restricted"}
        ), patch.object(appointment_routes, "update_appointment_status_service"), patch.object(
            settings_routes.settings_service, "create_faq", return_value={"id": "faq-2"}
        ):
            requests = (
                ("patch", "/api/flagged-conversations/45/review", {}),
                ("post", "/api/flagged-conversations/45/notes", {"note_text": "Checked"}),
                (
                    "patch",
                    "/api/flagged-conversations/45/confidentiality",
                    {"confidentiality_status": "restricted"},
                ),
                ("patch", "/api/appointments/17", {"status": "confirmed"}),
                ("post", "/api/settings/faqs", {"title": "T", "question": "Q", "answer": "A"}),
            )
            for method, path, payload in requests:
                with self.subTest(method=method, path=path):
                    self.assertLess(
                        getattr(self.client, method)(path, json=payload, headers=self._csrf_headers()).status_code,
                        300,
                    )

        self._authenticate("admin", 3)
        account = {"id": 88, "student_number": None, "staff_number": None}
        with patch.object(account_routes, "create_account_service", return_value=account):
            response = self.client.post(
                "/api/accounts",
                json={"full_name": "CSRF Test", "email": "csrf@example.test", "password": "Password123"},
                headers=self._csrf_headers(),
            )
        self.assertEqual(response.status_code, 201)

    def test_get_session_expiry_rbac_and_cors_remain_safe(self) -> None:
        from backend.server.routes import notification_routes

        self._authenticate("student")
        with patch.object(notification_routes, "list_notifications_service", return_value=[]):
            self.assertEqual(self.client.get("/api/notifications").status_code, 200)

        self.assertEqual(
            self.client.patch(
                "/api/flagged-conversations/9/review", headers=self._csrf_headers()
            ).status_code,
            403,
        )

        malicious = self.client.post(
            "/api/appointments",
            json={},
            headers={"Origin": "https://attacker.example"},
        )
        self.assertEqual(malicious.status_code, 403)
        self.assertEqual(malicious.get_json()["message"], "CSRF validation failed.")

        for response in (
            self.client.get("/health", headers={"Origin": "https://attacker.example"}),
            self.client.options(
                "/api/appointments",
                headers={
                    "Origin": "https://attacker.example",
                    "Access-Control-Request-Method": "POST",
                },
            ),
        ):
            self.assertNotIn("Access-Control-Allow-Origin", response.headers)
            self.assertNotIn("Access-Control-Allow-Credentials", response.headers)

        expired = self.app.test_client()
        with expired.session_transaction() as browser_session:
            browser_session["_csrf_token"] = "expired-token"
        response = expired.post("/api/appointments", json={})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["message"], "Login required.")


if __name__ == "__main__":
    unittest.main()
