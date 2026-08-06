from __future__ import annotations

import unittest
from types import SimpleNamespace

from backend.server.services.summary_service import SummaryService


class _FailedLlm:
    def generate(self, _prompt: str):  # type: ignore[no-untyped-def]
        return type("Result", (), {"success": False, "error": "unavailable"})()


class _CapturingLlm:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, prompt: str):  # type: ignore[no-untyped-def]
        self.prompts.append(prompt)
        return SimpleNamespace(
            success=True,
            text=(
                "The student asked about Guidance Office hours and reported feeling "
                "overwhelmed by schoolwork."
            ),
        )


class SummaryServiceTests(unittest.TestCase):
    def test_mixed_operational_and_emotional_evidence_is_required_in_summary_prompt(self) -> None:
        llm = _CapturingLlm()
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
        self.assertIn("distinct factual question and emotional concern", llm.prompts[0])
    def test_summary_failure_does_not_claim_raw_transcript_is_available(self) -> None:
        service = SummaryService(_FailedLlm())

        summary = service.generate_summary(
            student_name="Student",
            conversation=[{"from": "user", "text": "Private message"}],
            topic="academic",
            language="english",
            emotion="neutral",
            flagged=False,
        )

        self.assertIn("could not be generated", summary.summary)
        self.assertIn("recorded session", summary.summary)
        self.assertNotIn("conversation manually", summary.summary)
        self.assertNotIn("transcript", summary.summary)


if __name__ == "__main__":
    unittest.main()