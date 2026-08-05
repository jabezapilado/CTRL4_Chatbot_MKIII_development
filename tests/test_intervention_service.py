import unittest
from unittest.mock import patch

from backend.server.services import intervention_service


class InterventionServiceTests(unittest.TestCase):
    def setUp(self):
        self.case = {"id": 12, "escalation_status": "pending"}
        self.intervention = {
            "id": 5,
            "conversation_summary_id": 12,
            "staff_account_id": 3,
            "intervention_type": "Counseling Session",
            "objective": "Build a manageable support plan.",
            "progress_status": "planned",
            "outcome": None,
            "created_at": "2026-08-05T10:00:00",
            "updated_at": "2026-08-05T10:00:00",
        }

    def test_list_projects_interventions_without_internal_linkage(self):
        with patch.object(
            intervention_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            intervention_service,
            "list_interventions",
            return_value=[self.intervention],
        ), patch.object(
            intervention_service,
            "list_intervention_history",
            return_value=[
                {
                    "progress_status": "planned",
                    "outcome": None,
                    "created_at": "now",
                }
            ],
        ):
            interventions = intervention_service.list_staff_interventions(12)

        self.assertEqual(interventions[0]["intervention_type"], "Counseling Session")
        self.assertNotIn("conversation_summary_id", interventions[0])
        self.assertNotIn("staff_account_id", interventions[0])
        self.assertEqual(interventions[0]["history"][0]["progress_status"], "planned")

    def test_create_requires_supported_intervention_type(self):
        with patch.object(
            intervention_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), self.assertRaisesRegex(ValueError, "type is not supported"):
            intervention_service.create_staff_intervention(
                {"id": 3},
                12,
                "Medication Plan",
                "Provide support.",
            )

    def test_create_records_planned_intervention(self):
        with patch.object(
            intervention_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            intervention_service,
            "create_intervention",
            return_value=5,
        ) as create_intervention, patch.object(
            intervention_service,
            "fetch_intervention",
            return_value=self.intervention,
        ), patch.object(
            intervention_service,
            "list_intervention_history",
            return_value=[],
        ):
            intervention_service.create_staff_intervention(
                {"id": 3},
                12,
                "Counseling Session",
                " Build a manageable support plan. ",
            )

        create_intervention.assert_called_once_with(
            {
                "conversation_summary_id": 12,
                "staff_account_id": 3,
                "intervention_type": "Counseling Session",
                "objective": "Build a manageable support plan.",
                "progress_status": "planned",
            }
        )

    def test_progress_update_appends_history_for_scoped_intervention(self):
        updated_intervention = {**self.intervention, "progress_status": "ongoing"}
        with patch.object(
            intervention_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            intervention_service,
            "fetch_intervention",
            side_effect=[self.intervention, updated_intervention],
        ), patch.object(
            intervention_service,
            "update_intervention_progress",
            return_value=True,
        ) as update_progress, patch.object(
            intervention_service,
            "list_intervention_history",
            return_value=[],
        ):
            intervention_service.update_staff_intervention_progress(
                {"id": 3},
                12,
                5,
                "ongoing",
            )

        update_progress.assert_called_once_with(5, 12, 3, "ongoing")

    def test_outcome_requires_terminal_progress_status(self):
        with patch.object(
            intervention_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            intervention_service,
            "fetch_intervention",
            return_value=self.intervention,
        ), self.assertRaisesRegex(ValueError, "only after completion"):
            intervention_service.record_staff_intervention_outcome(
                {"id": 3},
                12,
                5,
                "Student agreed to the support plan.",
            )

    def test_outcome_is_recorded_once_after_completion(self):
        completed_intervention = {
            **self.intervention,
            "progress_status": "completed",
        }
        with_outcome = {
            **completed_intervention,
            "outcome": "Student completed the support plan.",
        }
        with patch.object(
            intervention_service,
            "fetch_flagged_conversation",
            return_value=self.case,
        ), patch.object(
            intervention_service,
            "fetch_intervention",
            side_effect=[completed_intervention, with_outcome],
        ), patch.object(
            intervention_service,
            "record_intervention_outcome",
            return_value=True,
        ) as record_outcome, patch.object(
            intervention_service,
            "list_intervention_history",
            return_value=[],
        ):
            intervention_service.record_staff_intervention_outcome(
                {"id": 3},
                12,
                5,
                " Student completed the support plan. ",
            )

        record_outcome.assert_called_once_with(
            5,
            12,
            3,
            "completed",
            "Student completed the support plan.",
        )


if __name__ == "__main__":
    unittest.main()