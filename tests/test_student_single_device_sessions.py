"""Regression coverage for the student-only single-device safeguard."""

from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import patch

from backend.server.services.student_session_service import StudentSessionService


class _MemoryCache:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    def get(self, key: str):
        return self.values.get(key)

    def set(self, key: str, value: object, timeout: int | None = None) -> None:
        del timeout
        self.values[key] = value

    def delete(self, key: str) -> None:
        self.values.pop(key, None)


class StudentSessionServiceTests(unittest.TestCase):
    def test_replacement_finalizes_the_existing_chat_with_its_server_context(self) -> None:
        service = StudentSessionService(cache=_MemoryCache(), timeout_seconds=900)
        self.assertTrue(service.register(41, "device-a-token", "device-a-session"))
        self.assertTrue(
            service.update_conversation_context(
                41,
                "device-a-token",
                topic="counseling",
                language="filipino",
                emotion="sadness",
                flagged=True,
                review_only=False,
                escalation_reason="Safety concern detected.",
                appointment={
                    "category": "Counseling",
                    "preferred_date": "2026-08-13",
                    "preferred_time_slot": "09:00",
                },
                active_summary_id=19,
            )
        )
        self.assertTrue(service.has_other_active_session(41, ""))

        class TransientChat:
            def __init__(self) -> None:
                self.cleared: tuple[str, int] | None = None

            def get_visible_history(self, session_id: str, account_id: int):
                assert session_id == "device-a-session"
                assert account_id == 41
                return [{"from": "user", "text": "I need support."}]

            def clear(self, session_id: str, account_id: int) -> None:
                self.cleared = (session_id, account_id)

        transient_chat = TransientChat()
        received: dict[str, object] = {}

        def finalizer(**kwargs):
            received.update(kwargs)
            return {"success": True, "status": "saved", "summary_id": 19}

        result = service.finalize_replaced_session(
            41,
            "",
            {"id": 41, "full_name": "Student Example"},
            transient_chat=transient_chat,
            finalizer=finalizer,
        )

        self.assertEqual(result, {"success": True, "status": "saved", "summary_id": 19})
        self.assertEqual(transient_chat.cleared, ("device-a-session", 41))
        self.assertEqual(received["topic"], "counseling")
        self.assertEqual(received["language"], "filipino")
        self.assertTrue(received["flagged"])
        self.assertEqual(received["active_summary_id"], 19)
        self.assertNotIn("I need support.", str(service._cache.values))

    def test_neutral_follow_up_does_not_overwrite_an_earlier_sadness_label(self) -> None:
        service = StudentSessionService(cache=_MemoryCache(), timeout_seconds=900)
        self.assertTrue(service.register(42, "device-token", "device-session"))
        self.assertTrue(
            service.update_conversation_context(
                42,
                "device-token",
                topic="general",
                language="english",
                emotion="Sadness",
                flagged=False,
                review_only=False,
                escalation_reason=None,
                appointment=None,
                active_summary_id=20,
            )
        )
        self.assertTrue(
            service.update_conversation_context(
                42,
                "device-token",
                topic="general",
                language="english",
                emotion="Neutral",
                flagged=False,
                review_only=False,
                escalation_reason=None,
                appointment=None,
                active_summary_id=20,
            )
        )

        stored = service._get(42)
        self.assertIsNotNone(stored)
        self.assertEqual(stored["conversation"]["emotion"], "Sadness")


class StudentSingleDeviceRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self._environment = patch.dict(
            os.environ,
            {
                "CHATBOT_SESSION_TYPE": "cachelib",
                "CHATBOT_SESSION_FILE_DIR": self._temporary_directory.name,
                "CHATBOT_SESSION_COOKIE_SECURE": "true",
            },
            clear=False,
        )
        self._environment.start()

        from backend.server import create_app

        with patch("backend.server.initialize_database"):
            self.app = create_app()
        self.app.config["TESTING"] = True

    def tearDown(self) -> None:
        self._environment.stop()
        self._temporary_directory.cleanup()

    @staticmethod
    def _csrf_headers(client) -> dict[str, str]:
        client.get("/login", base_url="https://localhost")
        with client.session_transaction() as browser_session:
            token = browser_session.get("_csrf_token")
        return {"X-CSRF-Token": str(token)}

    def _login(self, client, *, replace_existing_session: bool = False):
        return client.post(
            "/auth/login",
            json={
                "email": "student@example.test",
                "password": "not-persisted",
                "replace_existing_session": replace_existing_session,
            },
            base_url="https://localhost",
            headers=self._csrf_headers(client),
        )

    def test_student_replacement_finalizes_device_a_then_redirects_it_to_login(self) -> None:
        from backend.server import auth

        device_a = self.app.test_client()
        device_b = self.app.test_client()
        service = StudentSessionService(cache=_MemoryCache(), timeout_seconds=900)
        user = {
            "id": 82,
            "email": "student@example.test",
            "full_name": "Student Example",
            "role": "student",
        }

        with patch.object(auth, "student_session_service", service), patch.object(
            auth, "login_service", return_value=user
        ), patch.object(
            auth, "finalize_conversation", return_value={"success": True, "status": "saved"}
        ) as finalize, patch.object(
            auth.transient_chat_service,
            "get_visible_history",
            return_value=[{"from": "user", "text": "Server-owned chat"}],
        ), patch.object(auth.transient_chat_service, "clear") as clear_chat:
            self.assertEqual(self._login(device_a).status_code, 200)

            confirmation = self._login(device_b)
            self.assertEqual(confirmation.status_code, 409)
            self.assertFalse(confirmation.get_json()["success"])

            replacement = self._login(device_b, replace_existing_session=True)
            self.assertEqual(replacement.status_code, 200)
            self.assertTrue(replacement.get_json()["success"])
            finalize.assert_called_once()
            clear_chat.assert_called_once()

            old_device_status = device_a.get(
                "/auth/session-status",
                base_url="https://localhost",
            )
            self.assertEqual(old_device_status.status_code, 401)
            self.assertEqual(old_device_status.headers["X-CTRL4-Session-Replaced"], "1")

            old_device = device_a.get(
                "/chatbot",
                base_url="https://localhost",
                follow_redirects=False,
            )
            self.assertEqual(old_device.status_code, 302)
            self.assertEqual(old_device.headers["Location"], "/login?reason=session-required")

            new_device = device_b.get("/chatbot", base_url="https://localhost")
            self.assertEqual(new_device.status_code, 200)

    def test_staff_logins_remain_multi_device(self) -> None:
        from backend.server import auth

        staff_a = self.app.test_client()
        staff_b = self.app.test_client()
        service = StudentSessionService(cache=_MemoryCache(), timeout_seconds=900)
        staff = {
            "id": 83,
            "email": "staff@example.test",
            "full_name": "Staff Example",
            "role": "staff",
        }

        with patch.object(auth, "student_session_service", service), patch.object(
            auth, "login_service", return_value=staff
        ):
            self.assertEqual(
                staff_a.post(
                    "/auth/login",
                    json={"email": staff["email"], "password": "not-persisted"},
                    base_url="https://localhost",
                    headers=self._csrf_headers(staff_a),
                ).status_code,
                200,
            )
            self.assertEqual(
                staff_b.post(
                    "/auth/login",
                    json={"email": staff["email"], "password": "not-persisted"},
                    base_url="https://localhost",
                    headers=self._csrf_headers(staff_b),
                ).status_code,
                200,
            )


if __name__ == "__main__":
    unittest.main()
