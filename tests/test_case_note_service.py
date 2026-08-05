import unittest
from unittest.mock import patch

from backend.server.services import case_note_service


class CaseNoteServiceTests(unittest.TestCase):
    def setUp(self):
        self.case = {"id": 12, "escalation_status": "pending"}
        self.note = {
            "id": 7,
            "conversation_summary_id": 12,
            "staff_account_id": 3,
            "note_text": "Follow up during office hours.",
            "created_at": "2026-08-05T10:00:00",
            "updated_at": "2026-08-05T10:00:00",
        }

    def test_list_projects_notes_without_account_linkage(self):
        with patch.object(
            case_note_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            case_note_service,
            "list_case_notes",
            return_value=[self.note],
        ):
            notes = case_note_service.list_staff_case_notes(12)

        self.assertEqual(notes[0]["note_text"], self.note["note_text"])
        self.assertNotIn("conversation_summary_id", notes[0])
        self.assertNotIn("staff_account_id", notes[0])

    def test_create_requires_nonempty_note(self):
        with patch.object(
            case_note_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), self.assertRaisesRegex(ValueError, "Counselor note is required"):
            case_note_service.create_staff_case_note({"id": 3}, 12, "   ")

    def test_create_associates_note_with_staff_and_case(self):
        with patch.object(
            case_note_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            case_note_service,
            "create_case_note",
            return_value=7,
        ) as create_note, patch.object(
            case_note_service,
            "fetch_case_note",
            return_value=self.note,
        ):
            note = case_note_service.create_staff_case_note(
                {"id": 3},
                12,
                " Follow up during office hours. ",
            )

        self.assertEqual(note["id"], 7)
        create_note.assert_called_once_with(
            {
                "conversation_summary_id": 12,
                "staff_account_id": 3,
                "note_text": "Follow up during office hours.",
            }
        )

    def test_edit_rejects_note_from_another_case(self):
        with patch.object(
            case_note_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            case_note_service,
            "update_case_note",
            return_value=False,
        ), self.assertRaisesRegex(LookupError, "Counselor note not found"):
            case_note_service.update_staff_case_note(
                {"id": 3},
                12,
                99,
                "Updated note.",
            )


if __name__ == "__main__":
    unittest.main()