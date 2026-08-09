"""Regression coverage for the privacy-safe chatbot feedback loop."""

from __future__ import annotations

import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch


class ChatbotFeedbackRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self._environment = patch.dict(
            os.environ,
            {
                "CHATBOT_SESSION_TYPE": "cachelib",
                "CHATBOT_SESSION_FILE_DIR": self._temporary_directory.name,
                "CHATBOT_DATABASE_INITIALIZE_ON_START": "false",
            },
            clear=False,
        )
        self._environment.start()

        from backend.server import create_app

        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self._environment.stop()
        self._temporary_directory.cleanup()

    def _student_session(self, *, terms_accepted: bool = True) -> None:
        with self.client.session_transaction() as browser_session:
            browser_session["hau_user"] = {
                "id": 17,
                "email": "student17@example.test",
                "role": "student",
            }
            browser_session["student_terms_accepted"] = terms_accepted
            browser_session["_csrf_token"] = "feedback-csrf-token"
            browser_session["chatbot_feedback_response_tokens"] = [
                {
                    "token": "reply-token",
                    "summary_id": 81,
                    "response_context": "academics",
                }
            ]

    def _headers(self) -> dict[str, str]:
        return {"X-CSRF-Token": "feedback-csrf-token"}

    def test_student_feedback_uses_a_session_owned_token_once(self) -> None:
        from backend.server.routes import chatbot_routes

        self._student_session()
        with patch.object(chatbot_routes, "save_chatbot_feedback", return_value=44) as save:
            response = self.client.post(
                "/chat/feedback",
                json={
                    "response_token": "reply-token",
                    "category": "clear_useful",
                    "comment": "The reply was too generic.",
                },
                headers=self._headers(),
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["data"], {"feedback_id": 44})
        saved_payload = save.call_args.args[0]
        self.assertEqual(saved_payload["account_id"], 17)
        self.assertEqual(saved_payload["conversation_summary_id"], 81)
        self.assertEqual(saved_payload["category"], "clear_useful")
        self.assertEqual(saved_payload["response_context"], "academics")
        self.assertNotIn("response_text", saved_payload)
        self.assertNotIn("student_message", saved_payload)

        repeated = self.client.post(
            "/chat/feedback",
            json={"response_token": "reply-token", "category": "helpful"},
            headers=self._headers(),
        )
        self.assertEqual(repeated.status_code, 400)

    def test_feedback_requires_student_terms_and_valid_categories(self) -> None:
        self._student_session(terms_accepted=False)
        blocked = self.client.post(
            "/chat/feedback",
            json={"response_token": "reply-token", "category": "helpful"},
            headers=self._headers(),
        )
        self.assertEqual(blocked.status_code, 403)

        self._student_session()
        invalid = self.client.post(
            "/chat/feedback",
            json={"response_token": "reply-token", "category": "invalid_category"},
            headers=self._headers(),
        )
        self.assertEqual(invalid.status_code, 400)

    def test_feedback_mutation_keeps_central_csrf_protection(self) -> None:
        self._student_session()
        response = self.client.post(
            "/chat/feedback",
            json={"response_token": "reply-token", "category": "helpful"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["message"], "CSRF validation failed.")

    def test_feedback_context_is_server_derived_and_safety_overrides_topic(self) -> None:
        from backend.server.routes import chatbot_routes

        academic_result = SimpleNamespace(normalized_topic="academics")
        self.assertEqual(
            chatbot_routes._feedback_context_for_result(academic_result, False),
            "academics",
        )
        self.assertEqual(
            chatbot_routes._feedback_context_for_result(academic_result, True),
            "safety",
        )


if __name__ == "__main__":
    unittest.main()
