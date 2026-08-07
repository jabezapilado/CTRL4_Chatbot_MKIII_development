"""Application-level server-session checks without a MySQL dependency."""

from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import patch


class ApplicationSessionSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        environment = {
            "CHATBOT_SESSION_TYPE": "cachelib",
            "CHATBOT_SESSION_FILE_DIR": self._temporary_directory.name,
            "CHATBOT_SESSION_COOKIE_SECURE": "true",
        }
        self._environment = patch.dict(os.environ, environment, clear=False)
        self._environment.start()

        from backend.server import create_app

        with patch("backend.server.initialize_database"):
            self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self._environment.stop()
        self._temporary_directory.cleanup()

    def _cookie_value(self) -> str:
        cookie = self.client.get_cookie("ctrl4_session")
        self.assertIsNotNone(cookie)
        return cookie.value

    def _csrf_headers(self) -> dict[str, str]:
        with self.client.session_transaction() as browser_session:
            token = browser_session.get("_csrf_token")
        self.assertIsInstance(token, str)
        return {"X-CSRF-Token": token}

    def test_real_login_logout_and_role_guard_use_an_opaque_server_session(self) -> None:
        from backend.server import auth

        user = {
            "id": 71,
            "email": "security-student@example.test",
            "role": "student",
        }
        with self.client.session_transaction() as browser_session:
            browser_session["pre_auth"] = True
            browser_session["_csrf_token"] = "pre-auth-token"
        pre_login_cookie = self._cookie_value()

        with patch.object(auth, "login_service", return_value=user):
            login_response = self.client.post(
                "/auth/login",
                json={"email": user["email"], "password": "not-persisted"},
                base_url="https://localhost",
                headers=self._csrf_headers(),
            )

        login_cookie = self._cookie_value()
        set_cookie = login_response.headers.get("Set-Cookie", "")
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.get_json()["data"], user)
        self.assertNotEqual(pre_login_cookie, login_cookie)
        self.assertNotIn("hau_user", login_cookie)
        self.assertNotIn("conversation_escalated", login_cookie)
        self.assertNotIn("conversation_escalation_reason", login_cookie)
        self.assertIn("HttpOnly", set_cookie)
        self.assertIn("Secure", set_cookie)
        self.assertIn("SameSite=Lax", set_cookie)
        self.assertIn("Expires=", set_cookie)

        self.assertEqual(
            self.client.get("/chatbot", base_url="https://localhost").status_code,
            200,
        )
        dashboard_redirect = self.client.get(
            "/dashboard",
            base_url="https://localhost",
        )
        self.assertEqual(dashboard_redirect.status_code, 302)
        self.assertEqual(dashboard_redirect.headers["Location"], "/chatbot")
        forbidden = self.client.get(
            "/api/dashboard/appointments/analytics",
            base_url="https://localhost",
        )
        self.assertEqual(forbidden.status_code, 403)
        self.assertEqual(forbidden.get_json()["message"], "Staff access required.")

        self.assertEqual(
            self.client.post(
                "/auth/logout",
                base_url="https://localhost",
                headers=self._csrf_headers(),
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get("/chatbot", base_url="https://localhost").status_code,
            302,
        )

        invalid_client = self.app.test_client()
        invalid_client.set_cookie("ctrl4_session", login_cookie)
        self.assertEqual(
            invalid_client.get("/chatbot", base_url="https://localhost").status_code,
            302,
        )

    def test_logout_clears_server_owned_active_chat_before_session_invalidation(self) -> None:
        from backend.server import auth

        with self.client.session_transaction() as browser_session:
            browser_session["hau_user"] = {
                "id": 72,
                "email": "student72@example.test",
                "role": "student",
            }
            browser_session["_csrf_token"] = "logout-token"

        with patch.object(auth.transient_chat_service, "clear") as clear_active_chat:
            response = self.client.post(
                "/auth/logout",
                base_url="https://localhost",
                headers=self._csrf_headers(),
            )

        self.assertEqual(response.status_code, 200)
        clear_active_chat.assert_called_once()
        self.assertEqual(clear_active_chat.call_args.args[1], 72)
        self.assertEqual(
            self.client.get("/chatbot", base_url="https://localhost").status_code,
            302,
        )

    def test_student_chat_page_reads_only_bounded_server_owned_state_without_browser_cache(self) -> None:
        from backend.server.routes import frontend_routes

        with self.client.session_transaction() as browser_session:
            browser_session["hau_user"] = {
                "id": 73,
                "email": "student73@example.test",
                "role": "student",
            }

        with patch.object(
            frontend_routes.transient_chat_service,
            "get_visible_history",
            return_value=[{"from": "user", "text": "Current session message"}],
        ) as get_visible_history:
            response = self.client.get("/chatbot", base_url="https://localhost")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Cache-Control"), "no-store")
        self.assertIn(b'id="active-chat-state"', response.data)
        self.assertIn(b"Current session message", response.data)
        self.assertEqual(get_visible_history.call_args.args[1], 73)


if __name__ == "__main__":
    unittest.main()
