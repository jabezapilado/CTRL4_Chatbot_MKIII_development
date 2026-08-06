from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from flask import Flask

from backend.server.routes.chatbot_routes import chatbot_bp
from backend.server.services import conversation_service
from backend.server.services.summary_service import SummaryService
from backend.server.services.transient_chat_service import TransientChatService


class _Cache:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    def get(self, key: str):  # type: ignore[no-untyped-def]
        return self.values.get(key)

    def set(self, key: str, value: object, timeout: int) -> None:
        self.values[key] = value

    def delete(self, key: str) -> None:
        self.values.pop(key, None)


class _FailedLlm:
    def generate(self, _prompt: str):  # type: ignore[no-untyped-def]
        return SimpleNamespace(success=False, error="unavailable")


class ConversationFinalizationIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = Flask(__name__)
        self.app.secret_key = "finalization-integrity"
        self.app.register_blueprint(chatbot_bp)

    def _client(self, account_id: int = 1):
        client = self.app.test_client()
        with client.session_transaction() as session:
            session["hau_user"] = {
                "id": account_id,
                "email": f"student{account_id}@example.test",
                "full_name": f"Student {account_id}",
                "role": "student",
            }
        return client

    def test_assistant_greeting_only_skips_summary_and_persistence(self) -> None:
        greeting = [{"from": "bot", "text": "Welcome to CTRL4."}]
        with patch.object(
            conversation_service.summary_service,
            "generate_summary",
        ) as generate, patch.object(
            conversation_service,
            "save_conversation_summary",
        ) as save:
            result = conversation_service.finalize_conversation(
                user={"id": 1, "full_name": "Student"},
                conversation=greeting,
                topic="general",
                language="unknown",
                emotion="neutral",
                flagged=False,
            )

        self.assertEqual(result["status"], "skipped")
        self.assertEqual(result["student_message_count"], 0)
        generate.assert_not_called()
        save.assert_not_called()

    def test_finalize_route_ignores_appointment_only_browser_payload(self) -> None:
        client = self._client()
        with patch(
            "backend.server.routes.chatbot_routes.transient_chat_service.get_visible_history",
            return_value=[],
        ), patch(
            "backend.server.routes.chatbot_routes.finalize_conversation",
            return_value={"status": "skipped", "summary_id": None},
        ) as finalize, patch(
            "backend.server.routes.chatbot_routes.transient_chat_service.clear",
        ) as clear:
            response = client.post(
                "/chat/finalize",
                json={
                    "conversation": [
                        {"from": "bot", "text": "Welcome"},
                        {"from": "bot", "text": "Appointment submitted"},
                    ]
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"]["status"], "skipped")
        finalize.assert_called_once()
        self.assertEqual(finalize.call_args.kwargs["conversation"], [])
        clear.assert_called_once()

    def test_real_student_message_is_the_only_summary_evidence(self) -> None:
        summary = SimpleNamespace(
            primary_concern="appointment",
            conversation_type="general",
            emotion="neutral",
            flagged=False,
            appointment_recommendation=False,
            recommendations="No immediate intervention is required.",
            suggested_intervention="No immediate intervention is required.",
            language="english",
            total_messages=2,
            summary="Student requested an appointment.",
        )
        evidence = [
            {"from": "bot", "text": "Welcome"},
            {"from": "user", "text": "I want to book an appointment."},
            {"from": "bot", "text": "I can help with that."},
        ]
        with patch.object(
            conversation_service.summary_service,
            "generate_summary",
            return_value=summary,
        ) as generate, patch.object(
            conversation_service,
            "save_conversation_summary",
            return_value=17,
        ):
            result = conversation_service.finalize_conversation(
                user={"id": 1, "full_name": "Student"},
                conversation=evidence,
                topic="appointment",
                language="english",
                emotion="neutral",
                flagged=False,
            )

        forwarded = generate.call_args.kwargs["conversation"]
        self.assertEqual(result["status"], "saved")
        self.assertEqual(result["student_message_count"], 1)
        self.assertEqual(result["assistant_message_count"], 1)
        self.assertEqual(
            forwarded,
            [
                {"role": "user", "content": "I want to book an appointment."},
                {"role": "assistant", "content": "I can help with that."},
            ],
        )

    def test_empty_new_session_does_not_reuse_previous_account_evidence(self) -> None:
        cache = _Cache()
        transient = TransientChatService(cache=cache, timeout_seconds=60)
        transient.record_exchange("session-one", 1, [], "Real concern", "Reply")
        self.assertTrue(transient.get_visible_history("session-one", 1))
        self.assertEqual(transient.get_visible_history("session-two", 1), [])
        self.assertEqual(transient.get_visible_history("session-one", 2), [])

        with patch.object(conversation_service, "save_conversation_summary") as save:
            result = conversation_service.finalize_conversation(
                user={"id": 1, "full_name": "Student"},
                conversation=[],
                topic="general",
                language="unknown",
                emotion="neutral",
                flagged=False,
            )

        self.assertEqual(result["status"], "skipped")
        save.assert_not_called()

    def test_provider_failure_fallback_does_not_invent_clinical_or_academic_claims(self) -> None:
        service = SummaryService(_FailedLlm())
        summary = service.generate_summary(
            student_name="Student",
            conversation=[{"role": "user", "content": "I want to book an appointment."}],
            topic="appointment",
            language="english",
            emotion="neutral",
            flagged=False,
        )

        self.assertIn("could not be generated", summary.summary)
        for unsupported in ("anxiety", "distress", "overwhelm", "self-doubt", "academic pressure", "coping"):
            self.assertNotIn(unsupported, summary.summary.casefold())


if __name__ == "__main__":
    unittest.main()