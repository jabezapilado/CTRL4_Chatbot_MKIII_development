from __future__ import annotations

import re
import unittest
from types import SimpleNamespace

from backend.server.services.summary_service import SummaryService


class _FailedLlm:
    def generate(self, _prompt: str):  # type: ignore[no-untyped-def]
        return type("Result", (), {"success": False, "error": "unavailable"})()


class _CapturingLlm:
    def __init__(self, text: str = "Grounded summary.") -> None:
        self.prompts: list[str] = []
        self.text = text

    def generate(self, prompt: str):  # type: ignore[no-untyped-def]
        self.prompts.append(prompt)
        return SimpleNamespace(
            success=True,
            text=self.text,
        )


class _SequencedLlm:
    def __init__(self, *texts: str) -> None:
        self.prompts: list[str] = []
        self._texts = list(texts)

    def generate(self, prompt: str):  # type: ignore[no-untyped-def]
        self.prompts.append(prompt)
        return SimpleNamespace(
            success=True,
            text=self._texts.pop(0),
        )


class SummaryServiceTests(unittest.TestCase):
    def test_crisis_summary_and_recommendation_are_deterministic_and_high_priority(self) -> None:
        service = SummaryService(_FailedLlm())

        summary = service.generate_summary(
            student_name="Student",
            conversation=[{"from": "user", "text": "I wanna finish my life."}],
            topic="Crisis Concern",
            language="english",
            emotion="Crisis",
            flagged=True,
        )

        self.assertIn("suicidal ideation", summary.summary.casefold())
        self.assertIn("immediate safety response", summary.summary.casefold())
        self.assertIn("Immediate Guidance Office review", summary.recommendations)
        self.assertTrue(summary.flagged)

    def test_mixed_operational_and_emotional_evidence_is_required_in_summary_prompt(self) -> None:
        llm = _CapturingLlm(
            "The student asked about Guidance Office hours and reported feeling "
            "overwhelmed by schoolwork."
        )
        service = SummaryService(llm)
        message = (
            "What are your office hours? I'm feeling really overwhelmed lately "
            "because of my schoolwork and I don't know what to do."
        )

        summary = service.generate_summary(
            student_name="Student",
            conversation=[{"from": "user", "text": message}],
            topic="general",
            language="english",
            emotion="Fear",
            flagged=False,
        )

        self.assertIn("asked about Guidance Office hours", summary.summary)
        self.assertIn("overwhelmed by schoolwork", summary.summary)
        self.assertIn(message, llm.prompts[0])
        self.assertIn("each distinct factual question and emotional concern", llm.prompts[0])

    def test_generated_summary_repairs_unsupported_engagement_claims_and_quotes(self) -> None:
        for generated in (
            'The student "agreed" to continue talking and accepted help.',
            "The student provided the phone number 09171234567.",
        ):
            with self.subTest(generated=generated):
                summary = SummaryService(
                    _SequencedLlm(
                        generated,
                        "The student reported a wellbeing concern.",
                    )
                ).generate_summary(
                    student_name="Student",
                    conversation=[{"from": "user", "text": "I feel overwhelmed."}],
                    topic="general",
                    language="english",
                    emotion="Fear",
                    flagged=False,
                )

                self.assertEqual(summary.summary, "The student reported a wellbeing concern.")

    def test_routine_and_mixed_summaries_are_one_abstract_sentence(self) -> None:
        scenarios = (
            ("What are your office hours?", "The student asked about office hours."),
            ("I feel overwhelmed by deadlines.", "The student reported academic stress."),
            (
                "What are your office hours? I feel overwhelmed by schoolwork.",
                "The student asked about office hours and reported feeling overwhelmed by schoolwork.",
            ),
            (
                "I want to book an appointment because I feel anxious about my grades.",
                "The student requested an appointment and reported anxiety related to academic performance.",
            ),
        )
        for message, generated in scenarios:
            with self.subTest(message=message):
                summary = SummaryService(_CapturingLlm(generated + " Extra unsupported sentence.")).generate_summary(
                    student_name="Student",
                    conversation=[{"from": "user", "text": message}],
                    topic="general",
                    language="english",
                    emotion="Fear",
                    flagged=False,
                )
                self.assertEqual(summary.summary, generated)
                self.assertNotIn(message, summary.summary)

    def test_crisis_summaries_are_abstract_for_single_and_multi_turn_cases(self) -> None:
        for conversation in (
            [{"from": "user", "text": "I want to finish my life."}],
            [
                {"from": "user", "text": "I want to finish my life."},
                {"from": "bot", "text": "Safety response."},
                {"from": "user", "text": "okay"},
            ],
        ):
            with self.subTest(conversation=conversation):
                summary = SummaryService(_FailedLlm()).generate_summary(
                    student_name="Student",
                    conversation=conversation,
                    topic="Crisis Concern",
                    language="english",
                    emotion="Crisis",
                    flagged=True,
                )
                self.assertIn("expressed suicidal ideation", summary.summary)
                self.assertIn("immediate safety response", summary.summary)
                self.assertNotIn("finish my life", summary.summary)
                self.assertNotIn("okay", summary.summary)
                self.assertLessEqual(len(re.split(r"(?<=[.!?])\s+", summary.summary)), 2)
    def test_summary_failure_uses_an_abstract_privacy_safe_fallback(self) -> None:
        service = SummaryService(_FailedLlm())

        summary = service.generate_summary(
            student_name="Student",
            conversation=[{"from": "user", "text": "I am sad and my friends left me."}],
            topic="academic",
            language="english",
            emotion="neutral",
            flagged=False,
        )

        self.assertEqual(
            summary.summary,
            "The student reported sadness and distress following social disconnection from friends.",
        )
        self.assertNotIn("friends left me", summary.summary)
        self.assertNotIn("transcript", summary.summary)


if __name__ == "__main__":
    unittest.main()
