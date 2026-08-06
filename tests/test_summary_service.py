from __future__ import annotations

import unittest

from backend.server.services.summary_service import SummaryService


class _FailedLlm:
    def generate(self, _prompt: str):  # type: ignore[no-untyped-def]
        return type("Result", (), {"success": False, "error": "unavailable"})()


class SummaryServiceTests(unittest.TestCase):
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
        self.assertIn("available case metadata", summary.summary)
        self.assertNotIn("conversation manually", summary.summary)
        self.assertNotIn("transcript", summary.summary)


if __name__ == "__main__":
    unittest.main()