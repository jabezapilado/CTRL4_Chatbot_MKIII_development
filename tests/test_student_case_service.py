import unittest
from unittest.mock import patch

from backend.server.services import conversation_service


class StudentCaseServiceTests(unittest.TestCase):
    def test_student_case_projection_excludes_confidential_fields(self):
        rows = [
            {
                "id": 9,
                "account_id": 42,
                "summary": "Private counselor summary.",
                "emotion_results": "distressed",
                "escalation_reason": "Detected distressed emotion.",
                "staff_account_id": 5,
                "escalation_status": "pending",
                "submitted_at": "2026-08-05T10:00:00",
                "updated_at": "2026-08-05T10:00:00",
            }
        ]

        with patch.object(
            conversation_service,
            "list_student_case_statuses",
            return_value=rows,
        ) as list_statuses:
            cases = conversation_service.list_student_cases({"id": 42})

        list_statuses.assert_called_once_with(42)

        self.assertEqual(
            cases,
            [
                {
                    "case_status": "Submitted",
                    "submitted_at": "2026-08-05T10:00:00",
                    "updated_at": "2026-08-05T10:00:00",
                    "progress_text": "Your case has been received by the Guidance Office.",
                }
            ],
        )

    def test_reviewed_case_uses_student_safe_progress_text(self):
        with patch.object(
            conversation_service,
            "list_student_case_statuses",
            return_value=[
                {
                    "escalation_status": "reviewed",
                    "submitted_at": "2026-08-05T10:00:00",
                    "updated_at": "2026-08-05T11:00:00",
                }
            ],
        ):
            cases = conversation_service.list_student_cases({"id": 42})

        self.assertEqual(cases[0]["case_status"], "Reviewed")
        self.assertEqual(
            cases[0]["progress_text"],
            "Your case has been reviewed. The Guidance Office will contact you if further support is needed.",
        )

    def test_unknown_internal_status_uses_generic_progress_text(self):
        with patch.object(
            conversation_service,
            "list_student_case_statuses",
            return_value=[{"escalation_status": "resolved"}],
        ):
            cases = conversation_service.list_student_cases({"id": 42})

        self.assertEqual(cases[0]["case_status"], "In Progress")
        self.assertEqual(
            cases[0]["progress_text"],
            "Your case is being handled by the Guidance Office.",
        )


if __name__ == "__main__":
    unittest.main()