import unittest
from unittest.mock import patch

from backend.server.services import referral_service


class ReferralServiceTests(unittest.TestCase):
    def setUp(self):
        self.case = {"id": 12, "escalation_status": "pending"}
        self.referral = {
            "id": 4,
            "conversation_summary_id": 12,
            "staff_account_id": 3,
            "destination": "Psychologist",
            "referral_reason": "Needs specialized support.",
            "status": "pending",
            "created_at": "2026-08-05T10:00:00",
            "updated_at": "2026-08-05T10:00:00",
        }

    def test_list_projects_referrals_without_internal_linkage(self):
        with patch.object(
            referral_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            referral_service,
            "list_referrals",
            return_value=[self.referral],
        ), patch.object(
            referral_service,
            "list_referral_status_history",
            return_value=[{"status": "pending", "created_at": "now"}],
        ), patch.object(
            referral_service,
            "list_referral_notes",
            return_value=[],
        ):
            referrals = referral_service.list_staff_referrals(12)

        self.assertEqual(referrals[0]["destination"], "Psychologist")
        self.assertNotIn("conversation_summary_id", referrals[0])
        self.assertNotIn("staff_account_id", referrals[0])
        self.assertEqual(referrals[0]["status_history"][0]["status"], "pending")

    def test_create_requires_supported_destination(self):
        with patch.object(
            referral_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), self.assertRaisesRegex(ValueError, "destination is not supported"):
            referral_service.create_staff_referral(
                {"id": 3},
                12,
                "External Hospital",
                "Needs follow-up.",
            )

    def test_create_records_initial_status_and_optional_note(self):
        with patch.object(
            referral_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            referral_service,
            "create_referral",
            return_value=4,
        ) as create_referral, patch.object(
            referral_service,
            "fetch_referral",
            return_value=self.referral,
        ), patch.object(
            referral_service,
            "list_referral_status_history",
            return_value=[],
        ), patch.object(
            referral_service,
            "list_referral_notes",
            return_value=[],
        ):
            referral_service.create_staff_referral(
                {"id": 3},
                12,
                "Psychologist",
                " Needs specialized support. ",
                " Initial internal note. ",
            )

        create_referral.assert_called_once_with(
            {
                "conversation_summary_id": 12,
                "staff_account_id": 3,
                "destination": "Psychologist",
                "referral_reason": "Needs specialized support.",
                "status": "pending",
                "initial_note": "Initial internal note.",
            }
        )

    def test_status_update_appends_history_for_scoped_referral(self):
        updated_referral = {**self.referral, "status": "in_progress"}
        with patch.object(
            referral_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            referral_service,
            "fetch_referral",
            side_effect=[self.referral, updated_referral],
        ), patch.object(
            referral_service,
            "update_referral_status",
            return_value=True,
        ) as update_status, patch.object(
            referral_service,
            "list_referral_status_history",
            return_value=[],
        ), patch.object(
            referral_service,
            "list_referral_notes",
            return_value=[],
        ):
            referral_service.update_staff_referral_status(
                {"id": 3},
                12,
                4,
                "in_progress",
            )

        update_status.assert_called_once_with(4, 12, 3, "in_progress")

    def test_add_note_rejects_referral_from_another_case(self):
        with patch.object(
            referral_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            referral_service,
            "fetch_referral",
            return_value=None,
        ), self.assertRaisesRegex(LookupError, "Referral not found"):
            referral_service.add_staff_referral_note(
                {"id": 3},
                12,
                99,
                "Follow up with the destination.",
            )


if __name__ == "__main__":
    unittest.main()