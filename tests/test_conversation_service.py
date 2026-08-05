import unittest
from unittest.mock import patch

from backend.server.services import conversation_service


class ConversationServiceTests(unittest.TestCase):
    def test_staff_detail_excludes_transcript_and_linkage_fields(self):
        row = {
            "id": 8,
            "account_id": 42,
            "summary_id": 8,
            "primary_concern": "mental_health",
            "conversation_type": "general",
            "emotion_results": "distressed",
            "appointment_recommendation": "Guidance Office follow-up",
            "recommendations": "Contact the Guidance Office.",
            "suggested_intervention": "Contact the Guidance Office.",
            "language_used": "english",
            "total_messages": 2,
            "summary": "A confidential summary.",
            "created_at": "2026-08-05T10:00:00",
            "escalation_status": "pending",
            "escalation_reason": "Detected distressed emotion.",
            "reviewed_at": None,
        }

        with patch.object(
            conversation_service,
            "fetch_flagged_conversation",
            return_value=row,
        ):
            conversation = conversation_service.get_staff_flagged_conversation(8)

        self.assertNotIn("account_id", conversation)
        self.assertNotIn("summary_id", conversation)
        self.assertNotIn("transcript", conversation)

    def test_escalation_reason_uses_existing_normalized_emotion(self):
        reason = conversation_service.determine_escalation_reason(
            escalated=False,
            normalized_emotion="distressed",
        )

        self.assertEqual(reason, "Detected distressed emotion.")

    def test_review_is_idempotent_for_an_already_reviewed_conversation(self):
        reviewed = {"id": 8, "escalation_status": "reviewed"}

        with patch.object(
            conversation_service,
            "get_staff_flagged_conversation",
            return_value=reviewed,
        ) as get_conversation, patch.object(
            conversation_service,
            "mark_escalation_reviewed",
        ) as mark_reviewed:
            result = conversation_service.mark_staff_flagged_conversation_reviewed(8)

        self.assertEqual(result, reviewed)
        get_conversation.assert_called_once_with(8)
        mark_reviewed.assert_not_called()

    def test_review_rejects_non_pending_escalation(self):
        with patch.object(
            conversation_service,
            "get_staff_flagged_conversation",
            return_value={"id": 8, "escalation_status": "resolved"},
        ), self.assertRaisesRegex(
            ValueError,
            "cannot be marked as reviewed",
        ):
            conversation_service.mark_staff_flagged_conversation_reviewed(8)


if __name__ == "__main__":
    unittest.main()