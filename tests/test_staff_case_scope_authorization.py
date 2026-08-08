from __future__ import annotations

from contextlib import ExitStack
import unittest
from unittest.mock import patch

from flask import Flask

from backend.server.routes import conversation_routes
from backend.server.services import conversation_service


class StaffCaseScopeAuthorizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = Flask(__name__)
        self.app.secret_key = "staff-case-scope-test"
        self.app.register_blueprint(conversation_routes.conversation_bp)

    def _client_for(self, account_id: int, role: str = "staff"):
        client = self.app.test_client()
        with client.session_transaction() as session:
            session["hau_user"] = {
                "id": account_id,
                "email": f"{role}{account_id}@example.test",
                "role": role,
            }
        return client

    @staticmethod
    def _flagged_case(summary_id: int) -> dict:
        return {
            "summary_id": summary_id,
            "flagged_status": True,
            "review_status": "pending",
            "summary": "Approved case summary.",
        }

    @staticmethod
    def _request(client, method: str, path: str, payload: dict | None = None):
        return client.open(path, method=method, json=payload)

    def _service_patches(self, stack: ExitStack) -> dict[str, object]:
        return {
            "review": stack.enter_context(
                patch.object(
                    conversation_routes,
                    "mark_staff_flagged_conversation_reviewed",
                    return_value=self._flagged_case(101),
                )
            ),
            "confidentiality_read": stack.enter_context(
                patch.object(
                    conversation_routes,
                    "get_staff_case_confidentiality",
                    return_value={"confidentiality_status": "not_confidential"},
                )
            ),
            "confidentiality_write": stack.enter_context(
                patch.object(
                    conversation_routes,
                    "update_staff_case_confidentiality",
                    return_value={"confidentiality_status": "confidential"},
                )
            ),
            "notes_read": stack.enter_context(
                patch.object(conversation_routes, "list_staff_case_notes", return_value=[])
            ),
            "notes_create": stack.enter_context(
                patch.object(
                    conversation_routes,
                    "create_staff_case_note",
                    return_value={"id": 11, "note_text": "Approved note."},
                )
            ),
            "notes_update": stack.enter_context(
                patch.object(
                    conversation_routes,
                    "update_staff_case_note",
                    return_value={"id": 11, "note_text": "Updated note."},
                )
            ),
            "referrals_read": stack.enter_context(
                patch.object(conversation_routes, "list_staff_referrals", return_value=[])
            ),
            "referrals_create": stack.enter_context(
                patch.object(
                    conversation_routes,
                    "create_staff_referral",
                    return_value={"id": 12, "status": "pending"},
                )
            ),
            "referrals_update": stack.enter_context(
                patch.object(
                    conversation_routes,
                    "update_staff_referral_status",
                    return_value={"id": 12, "status": "in_progress"},
                )
            ),
            "referrals_note": stack.enter_context(
                patch.object(
                    conversation_routes,
                    "add_staff_referral_note",
                    return_value={"id": 12, "status": "pending"},
                )
            ),
            "interventions_read": stack.enter_context(
                patch.object(conversation_routes, "list_staff_interventions", return_value=[])
            ),
            "interventions_create": stack.enter_context(
                patch.object(
                    conversation_routes,
                    "create_staff_intervention",
                    return_value={"id": 13, "progress_status": "planned"},
                )
            ),
            "interventions_progress": stack.enter_context(
                patch.object(
                    conversation_routes,
                    "update_staff_intervention_progress",
                    return_value={"id": 13, "progress_status": "ongoing"},
                )
            ),
            "interventions_outcome": stack.enter_context(
                patch.object(
                    conversation_routes,
                    "record_staff_intervention_outcome",
                    return_value={"id": 13, "progress_status": "completed"},
                )
            ),
        }

    @staticmethod
    def _protected_requests(summary_id: int) -> list[tuple[str, str, int, dict | None]]:
        base = f"/api/flagged-conversations/{summary_id}"
        return [
            ("GET", base, 200, None),
            ("PATCH", f"{base}/review", 200, None),
            ("GET", f"{base}/confidentiality", 200, None),
            ("PATCH", f"{base}/confidentiality", 200, {
                "confidentiality_status": "confidential",
                "confidentiality_reason": "Approved reason.",
            }),
            ("GET", f"{base}/notes", 200, None),
            ("POST", f"{base}/notes", 201, {"note_text": "Approved note."}),
            ("PATCH", f"{base}/notes/11", 200, {"note_text": "Updated note."}),
            ("GET", f"{base}/referrals", 200, None),
            ("POST", f"{base}/referrals", 201, {
                "destination": "Guidance Office",
                "referral_reason": "Approved reason.",
            }),
            ("PATCH", f"{base}/referrals/12/status", 200, {"status": "in_progress"}),
            ("POST", f"{base}/referrals/12/notes", 201, {"note_text": "Approved note."}),
            ("GET", f"{base}/interventions", 200, None),
            ("POST", f"{base}/interventions", 201, {
                "intervention_type": "Check-in",
                "objective": "Approved objective.",
            }),
            ("PATCH", f"{base}/interventions/13/progress", 200, {
                "progress_status": "ongoing",
            }),
            ("PATCH", f"{base}/interventions/13/outcome", 200, {
                "outcome": "Approved outcome.",
            }),
        ]

    def test_out_of_scope_case_subresources_return_indistinguishable_not_found(self) -> None:
        client = self._client_for(1)
        with ExitStack() as stack:
            access = stack.enter_context(
                patch.object(conversation_routes, "get_staff_inbox_item", return_value=None)
            )
            service_mocks = self._service_patches(stack)

            for method, path, _, payload in self._protected_requests(202):
                with self.subTest(method=method, path=path):
                    response = self._request(client, method, path, payload)
                    self.assertEqual(response.status_code, 404)
                    self.assertEqual(
                        response.get_json(),
                        {
                            "success": False,
                            "message": "Flagged conversation not found.",
                            "errors": None,
                        },
                    )

            self.assertEqual(access.call_count, len(self._protected_requests(202)))
            for service_mock in service_mocks.values():
                service_mock.assert_not_called()

    def test_each_program_scope_can_access_only_its_own_case_subresources(self) -> None:
        def authorized_case(staff: dict, summary_id: int):
            if (staff["id"], summary_id) in {(1, 101), (2, 202)}:
                return self._flagged_case(summary_id)
            return None

        with ExitStack() as stack:
            stack.enter_context(
                patch.object(
                    conversation_routes,
                    "get_staff_inbox_item",
                    side_effect=authorized_case,
                )
            )
            self._service_patches(stack)
            for staff_id, own_summary_id, other_summary_id in ((1, 101, 202), (2, 202, 101)):
                client = self._client_for(staff_id)
                for method, path, expected, payload in self._protected_requests(own_summary_id):
                    with self.subTest(staff=staff_id, method=method, path=path):
                        response = self._request(client, method, path, payload)
                        self.assertEqual(response.status_code, expected)
                for method, path, _, payload in self._protected_requests(other_summary_id):
                    with self.subTest(staff=staff_id, denied_method=method, path=path):
                        self.assertEqual(
                            self._request(client, method, path, payload).status_code,
                            404,
                        )

    def test_legacy_staff_lists_receive_the_authenticated_staff_scope(self) -> None:
        client = self._client_for(1)
        expected = [{"id": 101, "summary": "Program A only."}]
        with patch.object(
            conversation_routes,
            "list_staff_inquiries",
            return_value=expected,
        ) as inquiries, patch.object(
            conversation_routes,
            "list_staff_conversation_summaries",
            return_value=expected,
        ) as summaries, patch.object(
            conversation_routes,
            "list_staff_escalations",
            return_value=expected,
        ) as escalations:
            for path, service in (
                ("/api/inquiries", inquiries),
                ("/api/conversation-summaries", summaries),
                ("/api/escalations", escalations),
            ):
                with self.subTest(path=path):
                    response = client.get(path)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.get_json()["data"]["items"], expected)
                    service.assert_called_once_with(
                        {"id": 1, "email": "staff1@example.test", "role": "staff"}
                    )

    def test_reviewed_case_history_uses_the_same_scope_as_inbox_detail(self) -> None:
        client = self._client_for(1)
        history = [
            {
                "summary_id": 99,
                "student_name": "Student One",
                "student_number": "2026-00001",
                "program": "Program A",
                "primary_concern": "crisis",
                "emotion_results": "Crisis",
                "flagged_status": True,
                "review_status": "reviewed",
                "created_at": "2026-08-05T09:00:00",
                "reviewed_at": "2026-08-05T10:00:00",
                "summary_preview": "Approved reviewed-case summary.",
            }
        ]
        with patch.object(
            conversation_routes,
            "list_staff_reviewed_case_history",
            return_value=history,
        ) as list_history:
            response = client.get("/api/staff/inbox/101/history")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"]["items"], history)
        self.assertEqual(response.headers.get("Cache-Control"), "no-store")
        list_history.assert_called_once_with(
            {"id": 1, "email": "staff1@example.test", "role": "staff"},
            101,
        )

        with patch.object(
            conversation_routes,
            "list_staff_reviewed_case_history",
            return_value=None,
        ):
            denied = client.get("/api/staff/inbox/202/history")

        self.assertEqual(denied.status_code, 404)
        self.assertEqual(
            denied.get_json(),
            {
                "success": False,
                "message": "Inbox item not found.",
                "errors": None,
            },
        )

        for role in ("student", "admin"):
            with self.subTest(role=role):
                self.assertEqual(
                    self._client_for(9, role).get("/api/staff/inbox/101/history").status_code,
                    403,
                )

    def test_legacy_staff_list_services_filter_using_assigned_programs(self) -> None:
        staff = {"id": 1, "role": "staff"}
        profile = {"id": 1, "assigned_programs": ["Program A"]}
        with patch.object(
            conversation_service,
            "fetch_account_by_id",
            return_value=profile,
        ), patch.object(
            conversation_service,
            "list_inquiries_for_programs",
            return_value=[{"id": 1, "account_id": 11}],
        ) as inquiries, patch.object(
            conversation_service,
            "list_conversation_summaries_for_programs",
            return_value=[{"id": 101, "account_id": 11}],
        ) as summaries, patch.object(
            conversation_service,
            "list_escalations_for_programs",
            return_value=[{"id": 201, "account_id": 11}],
        ) as escalations:
            self.assertEqual(conversation_service.list_staff_inquiries(staff)[0]["id"], 1)
            self.assertEqual(
                conversation_service.list_staff_conversation_summaries(staff)[0]["id"],
                101,
            )
            self.assertEqual(conversation_service.list_staff_escalations(staff)[0]["id"], 201)

        inquiries.assert_called_once_with(["program a"])
        summaries.assert_called_once_with(["program a"])
        escalations.assert_called_once_with(["program a"])

    def test_student_and_admin_roles_remain_denied_from_case_subresources(self) -> None:
        for role in ("student", "admin"):
            with self.subTest(role=role):
                response = self._client_for(9, role).get(
                    "/api/flagged-conversations/101/notes"
                )
                self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
