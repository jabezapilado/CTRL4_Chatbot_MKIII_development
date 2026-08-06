"""Focused log-capture regression coverage for protected chatbot content."""

from __future__ import annotations

import logging
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from flask import Flask

from backend.server.routes.chatbot_routes import chatbot_bp
from backend.server.services.ai_service import AIService
from backend.server.services.emotion_service import EmotionPrediction
from backend.server.services.language_service import LanguagePrediction
from backend.server.services.metadata_service import ConversationMetadata
from backend.server.services.response_safety_service import ResponseSafetyResult
from backend.server.services.safety_service import SafetyResult


SENTINEL = "PRIVATE-CHAT-SENTINEL-DO-NOT-LOG"


class _Language:
    def detect(self, _message: str) -> LanguagePrediction:
        return LanguagePrediction(language="english", confidence=1.0)


class _Safety:
    def __init__(self, response: str | None = None) -> None:
        self.response = response

    def check(self, _message: str, language: str) -> SafetyResult:
        return SafetyResult(
            safe=True,
            should_escalate=False,
            response=self.response,
        )


class _Intent:
    def detect(self, _message: str) -> str:
        return "faq"


class _Topic:
    def classify(self, _message: str) -> str:
        return "general_inquiry"


class _Metadata:
    def extract(self, _message: str) -> ConversationMetadata:
        return ConversationMetadata()


class _Emotion:
    def predict(self, _message: str) -> EmotionPrediction:
        return EmotionPrediction(
            emotion="Neutral",
            sentiment="neutral",
            confidence=1.0,
            is_negative=False,
            normalized_emotion="neutral",
        )


class _Rag:
    ready = False


class _PromptBuilder:
    def __init__(self, failure: Exception | None = None) -> None:
        self.failure = failure

    def build(self, _input: object) -> str:
        if self.failure:
            raise self.failure
        return "safe prompt"


class _Llm:
    def generate(self, _prompt: str) -> SimpleNamespace:
        return SimpleNamespace(success=True, text="A safe response.", error=None)


class _ResponseSafety:
    def validate(
        self,
        _response: str,
        _documents: list[object],
    ) -> ResponseSafetyResult:
        return ResponseSafetyResult(allowed=True)


def _service(
    *,
    safety_response: str | None = None,
    prompt_failure: Exception | None = None,
) -> AIService:
    return AIService(
        safety=_Safety(safety_response),
        language=_Language(),
        emotion=_Emotion(),
        rag=_Rag(),
        prompt_builder=_PromptBuilder(prompt_failure),
        llm=_Llm(),
        intent=_Intent(),
        topic_classifier=_Topic(),
        metadata_extractor=_Metadata(),
        response_safety=_ResponseSafety(),
    )


class ProtectedChatLoggingTests(unittest.TestCase):
    def _assert_no_sentinel(self, records: list[str]) -> None:
        self.assertNotIn(SENTINEL, "\n".join(records))

    def test_successful_chat_and_prompt_construction_do_not_log_content(self) -> None:
        with self.assertLogs("backend.server.services.ai_service", logging.DEBUG) as logs:
            result = _service().respond(
                SENTINEL,
                conversation=[{"from": "user", "text": SENTINEL}],
            )

        self.assertTrue(result.success)
        self._assert_no_sentinel(logs.output)

    def test_ai_failure_does_not_log_content_embedded_in_exception(self) -> None:
        with self.assertLogs("backend.server.services.ai_service", logging.ERROR) as logs:
            result = _service(
                prompt_failure=RuntimeError(f"prompt failed: {SENTINEL}"),
            ).respond(SENTINEL, conversation=[{"from": "user", "text": SENTINEL}])

        self.assertFalse(result.success)
        self._assert_no_sentinel(logs.output)
        self.assertIn("exception_type=RuntimeError", "\n".join(logs.output))

    def test_safety_short_circuit_does_not_log_content(self) -> None:
        with self.assertLogs("backend.server.services.ai_service", logging.DEBUG) as logs:
            result = _service(safety_response="Contact the Guidance Office.").respond(
                SENTINEL,
                conversation=[{"from": "user", "text": SENTINEL}],
            )

        self.assertTrue(result.success)
        self._assert_no_sentinel(logs.output)

    def test_finalization_failure_does_not_log_conversation_or_user_identifiers(self) -> None:
        app = Flask(__name__)
        app.config.update(TESTING=True, SECRET_KEY="test-secret-key")
        app.register_blueprint(chatbot_bp)
        client = app.test_client()
        with client.session_transaction() as browser_session:
            browser_session["hau_user"] = {
                "id": 987,
                "email": "student@example.test",
                "role": "student",
            }

        with patch(
            "backend.server.routes.chatbot_routes.finalize_conversation",
            side_effect=RuntimeError(f"finalization failed: {SENTINEL}"),
        ), patch(
            "backend.server.routes.chatbot_routes.transient_chat_service.get_visible_history",
            return_value=[{"from": "user", "text": SENTINEL}],
        ):
            with self.assertLogs(
                "backend.server.routes.chatbot_routes", logging.ERROR
            ) as logs:
                response = client.post(
                    "/chat/finalize",
                    json={
                        "conversation": [{"from": "user", "text": SENTINEL}],
                    },
                )

        self.assertEqual(response.status_code, 500)
        self._assert_no_sentinel(logs.output)
        self.assertNotIn("987", "\n".join(logs.output))


if __name__ == "__main__":
    unittest.main()
