import unittest
from unittest.mock import patch

from backend.server.services import confidentiality_service


class ConfidentialityServiceTests(unittest.TestCase):
    def setUp(self):
        self.case = {"id": 12, "escalation_status": "pending"}
        self.confidentiality = {
            "id": 6,
            "conversation_summary_id": 12,
            "staff_account_id": 3,
            "confidentiality_status": "confidential",
            "confidentiality_reason": "Sensitive safeguarding concern.",
            "created_at": "2026-08-05T10:00:00",
            "updated_at": "2026-08-05T10:00:00",
        }

    def test_get_projects_current_state_without_internal_linkage(self):
        with patch.object(
            confidentiality_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            confidentiality_service,
            "fetch_case_confidentiality",
            return_value=self.confidentiality,
        ), patch.object(
            confidentiality_service,
            "list_case_confidentiality_history",
            return_value=[
                {
                    "confidentiality_status": "confidential",
                    "confidentiality_reason": "Sensitive safeguarding concern.",
                    "created_at": "now",
                }
            ],
        ):
            result = confidentiality_service.get_staff_case_confidentiality(12)

        self.assertEqual(result["confidentiality_status"], "confidential")
        self.assertNotIn("conversation_summary_id", result)
        self.assertNotIn("staff_account_id", result)
        self.assertEqual(result["history"][0]["confidentiality_status"], "confidential")

    def test_marking_confidential_requires_reason(self):
        with patch.object(
            confidentiality_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), self.assertRaisesRegex(ValueError, "reason is required"):
            confidentiality_service.update_staff_case_confidentiality(
                {"id": 3},
                12,
                "confidential",
                " ",
            )

    def test_first_confidentiality_transition_creates_record_and_history(self):
        with patch.object(
            confidentiality_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            confidentiality_service,
            "fetch_case_confidentiality",
            side_effect=[None, self.confidentiality],
        ), patch.object(
            confidentiality_service,
            "create_case_confidentiality",
        ) as create_confidentiality, patch.object(
            confidentiality_service,
            "list_case_confidentiality_history",
            return_value=[],
        ):
            confidentiality_service.update_staff_case_confidentiality(
                {"id": 3},
                12,
                "confidential",
                " Sensitive safeguarding concern. ",
            )

        create_confidentiality.assert_called_once_with(
            {
                "conversation_summary_id": 12,
                "staff_account_id": 3,
                "confidentiality_status": "confidential",
                "confidentiality_reason": "Sensitive safeguarding concern.",
            }
        )

    def test_removal_appends_not_confidential_transition(self):
        removed_confidentiality = {
            **self.confidentiality,
            "confidentiality_status": "not_confidential",
            "confidentiality_reason": None,
        }
        with patch.object(
            confidentiality_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            confidentiality_service,
            "fetch_case_confidentiality",
            side_effect=[self.confidentiality, removed_confidentiality],
        ), patch.object(
            confidentiality_service,
            "update_case_confidentiality",
            return_value=True,
        ) as update_confidentiality, patch.object(
            confidentiality_service,
            "list_case_confidentiality_history",
            return_value=[],
        ):
            confidentiality_service.update_staff_case_confidentiality(
                {"id": 3},
                12,
                "not_confidential",
            )

        update_confidentiality.assert_called_once_with(
            12,
            3,
            "not_confidential",
            None,
        )

    def test_update_rejects_same_confidentiality_status(self):
        with patch.object(
            confidentiality_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            confidentiality_service,
            "fetch_case_confidentiality",
            return_value=self.confidentiality,
        ), self.assertRaisesRegex(ValueError, "already has that confidentiality status"):
            confidentiality_service.update_staff_case_confidentiality(
                {"id": 3},
                12,
                "confidential",
                "New reason.",
            )


if __name__ == "__main__":
    unittest.main()