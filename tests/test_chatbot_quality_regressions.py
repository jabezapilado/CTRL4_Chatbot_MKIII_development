"""Focused regressions for conversational quality without live providers."""

from __future__ import annotations

import importlib
import sys
import types
import unittest
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SERVICES_DIR = ROOT / "backend/server/services"
PACKAGE = "chatbot_quality_test.server.services"


def _load_service_module(name: str) -> types.ModuleType:
    """Load a service without executing the eager production registry."""

    if PACKAGE not in sys.modules:
        root_package = types.ModuleType("chatbot_quality_test")
        root_package.__path__ = []
        server_package = types.ModuleType("chatbot_quality_test.server")
        server_package.__path__ = []
        services_package = types.ModuleType(PACKAGE)
        services_package.__path__ = [str(SERVICES_DIR)]
        config = types.ModuleType("chatbot_quality_test.server.config")
        config.Config = object
        db = types.ModuleType("chatbot_quality_test.server.db")
        db.get_staff_by_program = lambda _program: None
        db.get_student_by_id = lambda _account_id: None
        db.load_persisted_settings = lambda _keys: {}
        providers = types.ModuleType("chatbot_quality_test.server.llm_providers")
        providers.BaseProvider = object
        providers.GeminiProvider = object
        providers.OllamaProvider = object
        providers.LLMResponse = object
        sys.modules[root_package.__name__] = root_package
        sys.modules[server_package.__name__] = server_package
        sys.modules[services_package.__name__] = services_package
        sys.modules[config.__name__] = config
        sys.modules[db.__name__] = db
        sys.modules[providers.__name__] = providers

    return importlib.import_module(f"{PACKAGE}.{name}")


AIService = _load_service_module("ai_service").AIService
EmotionPrediction = _load_service_module("emotion_service").EmotionPrediction
IntentService = _load_service_module("intent_service").IntentService
LanguagePrediction = _load_service_module("language_service").LanguagePrediction
ConversationMetadata = _load_service_module("metadata_service").ConversationMetadata
PromptBuilder = _load_service_module("prompt_builder").PromptBuilder
ResponseSafetyResult = _load_service_module(
    "response_safety_service"
).ResponseSafetyResult
ResponseSafetyService = _load_service_module(
    "response_safety_service"
).ResponseSafetyService
ResponseValidator = _load_service_module("response_validator").ResponseValidator
OperationalGuidanceService = _load_service_module(
    "operational_guidance_service"
).OperationalGuidanceService
SafetyResult = _load_service_module("safety_service").SafetyResult
SafetyService = _load_service_module("safety_service").SafetyService
TopicService = _load_service_module("topic_service").TopicService


FIRST_MESSAGE = "I'm taking CONWORLD, I hate it so much haha."
FOLLOW_UP = "It's just I'm tired of doing stuff in that subject."


class _Language:
    def detect(self, _message: str) -> LanguagePrediction:
        return LanguagePrediction(language="english", confidence=1.0)


class _Safety:
    def check(self, _message: str, language: str = "english") -> SafetyResult:
        return SafetyResult(safe=True, should_escalate=False)


@dataclass
class _Metadata:
    def extract(self, _message: str) -> ConversationMetadata:
        return ConversationMetadata()


class _Rag:
    ready = False


class _RetrievedRag:
    ready = True

    def __init__(self, documents: list[object]) -> None:
        self.documents = documents
        self.queries: list[str] = []

    def retrieve(self, query: str) -> list[object]:
        self.queries.append(query)
        return self.documents


class _Emotion:
    def __init__(self, normalized_emotion: str = "negative") -> None:
        self.normalized_emotion = normalized_emotion

    def predict(self, _message: str) -> EmotionPrediction:
        return EmotionPrediction(
            emotion="Anger" if self.normalized_emotion == "negative" else "Fear",
            sentiment="Negative",
            confidence=0.92,
            is_negative=True,
            normalized_emotion=self.normalized_emotion,
        )


class _CapturingLlm:
    def __init__(self, responses: list[str]) -> None:
        self.responses = iter(responses)
        self.prompts: list[str] = []

    def generate(self, prompt: str):  # type: ignore[no-untyped-def]
        self.prompts.append(prompt)
        return type("Result", (), {"success": True, "text": next(self.responses)})()


class _AllowResponses:
    def validate(self, _response: str, _documents: list[object]) -> ResponseSafetyResult:
        return ResponseSafetyResult(allowed=True)


def _service(
    llm: _CapturingLlm,
    *,
    emotion: _Emotion | None = None,
    safety: object | None = None,
    rag: object | None = None,
    response_safety: object | None = None,
    operational_guidance: object | None = None,
) -> AIService:
    return AIService(
        safety=safety or _Safety(),
        language=_Language(),
        emotion=emotion or _Emotion(),
        rag=rag or _Rag(),
        prompt_builder=PromptBuilder(),
        llm=llm,
        intent=IntentService(),
        topic_classifier=TopicService(),
        metadata_extractor=_Metadata(),
        response_safety=response_safety or _AllowResponses(),
        operational_guidance=operational_guidance,
    )


class ResponseValidationRegressionTests(unittest.TestCase):
    def test_common_empathy_wording_is_not_rejected(self) -> None:
        valid, reason = ResponseValidator().validate(
            "It sounds like that subject has been draining your energy. "
            "Would practical study ideas or a chance to vent help more?",
            [{"from": "bot", "text": "It sounds like you have a lot going on."}],
        )

        self.assertTrue(valid)
        self.assertEqual(reason, "")

    def test_empty_and_exact_duplicate_responses_are_rejected(self) -> None:
        validator = ResponseValidator()
        self.assertEqual(
            validator.validate("   ", []),
            (False, "The response is empty."),
        )
        self.assertEqual(
            validator.validate(None, []),  # type: ignore[arg-type]
            (False, "The response is malformed."),
        )
        repeated = "Let us make a small plan for the next study session."
        self.assertEqual(
            validator.validate(repeated, [{"from": "bot", "text": repeated}]),
            (False, "Repeated response detected."),
        )

    def test_post_generation_safety_still_blocks_unsafe_provider_output(self) -> None:
        llm = _CapturingLlm(["You should hurt yourself to make it stop."])
        result = _service(llm, response_safety=ResponseSafetyService()).respond(
            "I am having a difficult day."
        )

        self.assertTrue(result.success)
        self.assertNotIn("hurt yourself", result.response.casefold())
        self.assertIn("contact a trusted person", result.response.casefold())

    def test_unverified_generic_institution_name_is_replaced(self) -> None:
        result = ResponseSafetyService().validate(
            "The University Guidance Center can help with your concern.",
            [SimpleNamespace(text="The SOC Guidance Office is open Monday to Friday.")],
        )

        self.assertFalse(result.allowed)
        self.assertEqual(result.category, "fabricated_institutional_information")


class ConversationHistoryRegressionTests(unittest.TestCase):
    def test_live_office_hours_bypass_rag_and_provider_prior_knowledge(self) -> None:
        settings = {"officeHours": "Monday to Friday, 9:00 AM to 4:00 PM"}
        operational = OperationalGuidanceService(
            load_settings=lambda _keys: settings,
            fetch_student=lambda _account_id: {"program": "BSCS"},
            fetch_staff_for_program=lambda _program: None,
        )
        llm = _CapturingLlm(["An unrelated provider answer that must not be used."])
        rag = _RetrievedRag([SimpleNamespace(source="legacy.md", text="Wrong hours")])

        result = _service(
            llm,
            rag=rag,
            operational_guidance=operational,
            response_safety=_AllowResponses(),
        ).respond("What are your office hours?", user={"id": 7, "role": "student"})

        self.assertEqual(
            result.response,
            "The current SOC Guidance Office hours are: Monday to Friday, 9:00 AM to 4:00 PM.",
        )
        self.assertEqual(llm.prompts, [])
        self.assertEqual(rag.queries, [])

    def test_missing_live_operational_setting_is_never_filled_by_provider_or_rag(self) -> None:
        operational = OperationalGuidanceService(
            load_settings=lambda _keys: {},
            fetch_student=lambda _account_id: {"program": "BSCS"},
            fetch_staff_for_program=lambda _program: None,
        )
        llm = _CapturingLlm(["Invented office hours."])

        result = _service(
            llm,
            operational_guidance=operational,
            response_safety=_AllowResponses(),
        ).respond("What are your office hours?", user={"id": 7, "role": "student"})

        self.assertIn("not currently configured", result.response)
        self.assertIn("confirm it with the SOC Guidance Office", result.response)
        self.assertEqual(llm.prompts, [])

    def test_live_availability_and_counselor_projection_exclude_internal_staff_fields(self) -> None:
        operational = OperationalGuidanceService(
            load_settings=lambda _keys: {
                "appointmentAvailability": {
                    "officeAvailability": [{"days": "Monday", "time": "9:00 AM - 12:00 PM"}],
                    "holidays": [],
                    "academicCalendarExclusions": [],
                    "unavailableDates": [],
                }
            },
            fetch_student=lambda _account_id: {"program": "BSCS"},
            fetch_staff_for_program=lambda _program: {
                "id": 91,
                "full_name": "Guidance Staff",
                "email": "private@example.test",
                "assigned_programs": ["BSCS"],
                "office": "Room 101",
                "consultation_schedules": [
                    {"room": "Room 101", "days": "Monday", "time": "9:00 AM - 12:00 PM"}
                ],
            },
        )

        availability = operational.answer(
            "What appointment times are available?", {"id": 7, "role": "student"}
        )
        counselor = operational.answer(
            "Who can I speak with?", {"id": 7, "role": "student"}
        )

        self.assertIsNotNone(availability)
        self.assertIn("Monday: 9:00 AM - 12:00 PM", availability.response)
        self.assertIsNotNone(counselor)
        self.assertIn("Guidance Staff", counselor.response)
        self.assertNotIn("91", counselor.response)
        self.assertNotIn("private@example.test", counselor.response)
        self.assertNotIn("BSCS", counselor.response)

    def test_unconfigured_appointment_duration_is_not_invented(self) -> None:
        operational = OperationalGuidanceService(
            load_settings=lambda _keys: {},
            fetch_student=lambda _account_id: {"program": "BSCS"},
            fetch_staff_for_program=lambda _program: None,
        )

        answer = operational.answer(
            "How long is a counseling appointment?", {"id": 7, "role": "student"}
        )

        self.assertIsNotNone(answer)
        self.assertIn("Appointment duration is not currently configured", answer.response)

    def test_office_hours_retrieval_is_injected_and_grounded_in_the_final_response(self) -> None:
        official_chunk = (
            "The SOC Guidance Office is open Monday to Friday, 8:00 AM to 5:00 PM. "
            "It is closed on weekends and public holidays."
        )
        rag = _RetrievedRag(
            [
                SimpleNamespace(
                    source="office_hours.json",
                    text=official_chunk,
                    score=0.99,
                )
            ]
        )
        llm = _CapturingLlm([
            "The SOC Guidance Office is open Monday to Friday, 8:00 AM to 5:00 PM."
        ])

        result = _service(llm, rag=rag, response_safety=ResponseSafetyService()).respond(
            "What are your office hours?"
        )

        self.assertEqual(rag.queries, ["What are your office hours?"])
        self.assertIn("[Source: office_hours.json]", llm.prompts[0])
        self.assertIn(official_chunk, llm.prompts[0])
        self.assertIn("Use the institution names exactly", llm.prompts[0])
        self.assertEqual(
            result.response,
            "The SOC Guidance Office is open Monday to Friday, 8:00 AM to 5:00 PM.",
        )
        self.assertNotIn("University Guidance Center", result.response)

    def test_taglish_appointment_request_uses_retrieved_appointment_context(self) -> None:
        official_chunk = (
            "Students may book a counseling appointment directly through CTRL4. "
            "The appointment booking feature allows students to request a date and time slot."
        )
        rag = _RetrievedRag(
            [
                SimpleNamespace(
                    source="appointment_process.json",
                    text=official_chunk,
                    score=0.98,
                )
            ]
        )
        llm = _CapturingLlm([
            "Maaari kang mag-request ng appointment sa CTRL4 at pumili ng available na date at time slot."
        ])

        result = _service(llm, rag=rag, response_safety=ResponseSafetyService()).respond(
            "Paano ako mag-book ng appointment?"
        )

        self.assertEqual(rag.queries, ["Paano ako mag-book ng appointment?"])
        self.assertIn(official_chunk, llm.prompts[0])
        self.assertEqual(result.intent, "appointment_booking")
        self.assertIn("CTRL4", result.response)

    def test_browser_history_is_normalized_into_the_prompt_and_preserves_continuity(self) -> None:
        first_reply = (
            "It sounds like CONWORLD has become exhausting. Would practical study "
            "ideas, a chance to vent, or Guidance support be most useful right now?"
        )
        follow_up_reply = (
            "That makes sense after carrying so much work in the same subject. "
            "We can look at one smaller task to make the next session more manageable."
        )
        llm = _CapturingLlm([first_reply, follow_up_reply])
        service = _service(llm)

        first = service.respond(
            FIRST_MESSAGE,
            conversation=[{"from": "bot", "text": "Welcome. How can I help today?"}],
        )
        history = [
            {"from": "bot", "text": "Welcome. How can I help today?"},
            {"from": "user", "text": FIRST_MESSAGE},
            {"from": "bot", "text": first.response},
            {"from": "malformed", "text": "ignore me"},
            {"from": "user", "text": "   "},
        ]
        follow_up = service.respond(FOLLOW_UP, conversation=history)

        self.assertEqual(first.topic, "Academics")
        self.assertEqual(first.normalized_topic, "academics")
        self.assertEqual(follow_up.state, "Exploring Concern")
        self.assertFalse(first.escalated)
        self.assertFalse(follow_up.escalated)
        self.assertEqual(follow_up.response, follow_up_reply)
        self.assertIn(f"User: {FIRST_MESSAGE}", llm.prompts[1])
        self.assertIn(f"Assistant: {first_reply}", llm.prompts[1])
        self.assertNotIn("User: \n", llm.prompts[1])

    def test_appointment_transition_keeps_existing_intent(self) -> None:
        llm = _CapturingLlm([
            "You can use the appointment booking option to choose an available date and time."
        ])
        result = _service(llm).respond("I wanna book an appointment.")

        self.assertTrue(result.success)
        self.assertEqual(result.intent, "appointment_booking")


class EscalationRegressionTests(unittest.TestCase):
    def test_routine_academic_frustration_is_not_escalated(self) -> None:
        routine_messages = (
            FIRST_MESSAGE,
            FOLLOW_UP,
            "Pagod ako sa subject na ito.",
            "Nakakainis itong assignment.",
        )
        service = _service(
            _CapturingLlm(
                [
                    "That subject sounds frustrating. We can talk through a practical next step."
                    for _ in routine_messages
                ]
            )
        )

        for message in routine_messages:
            with self.subTest(message=message):
                result = service.respond(message)
                self.assertFalse(result.escalated)
                self.assertEqual(result.normalized_emotion, "negative")

    def test_distressed_and_crisis_signals_remain_escalation_eligible(self) -> None:
        distressed = _service(
            _CapturingLlm(["I am here with you."]),
            emotion=_Emotion("distressed"),
        ).respond("I feel overwhelmed and need support.")
        crisis = _service(
            _CapturingLlm(["unused"]),
            safety=SafetyService(),
        ).respond("I want to die.")

        self.assertTrue(distressed.escalated)
        self.assertTrue(crisis.escalated)
        self.assertEqual(crisis.normalized_emotion, "crisis")

    def test_ambiguous_filipino_fatigue_requires_additional_high_risk_evidence(self) -> None:
        safety = SafetyService()
        for text in ("Pagod na pagod na ako.", "Ayoko na.", "Suko na ako."):
            with self.subTest(text=text):
                self.assertFalse(safety.check(text, language="filipino").should_escalate)

        self.assertTrue(
            safety.check(
                "Pagod na pagod na ako at gusto ko nang mawala.",
                language="filipino",
            ).should_escalate
        )
        self.assertTrue(
            safety.check(
                "Ayoko na, gusto kong mamatay.",
                language="filipino",
            ).should_escalate
        )


if __name__ == "__main__":
    unittest.main()
