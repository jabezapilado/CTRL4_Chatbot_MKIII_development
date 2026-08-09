from __future__ import annotations

import unittest
from unittest.mock import patch
from flask import Flask

from backend.server.services import account_service


class AccountBoundaryTests(unittest.TestCase):
    def test_verified_profile_seed_uses_only_documented_rooms_and_schedule_windows(self) -> None:
        from backend.server import db

        self.assertEqual(db.APPROVED_CONSULTATION_ROOMS, ("SJH-206", "PGN-105"))
        self.assertEqual(
            db.APPROVED_CONSULTATION_SCHEDULES,
            (
                {"room": "SJH-206", "days": "Monday-Friday", "time": "7:00 AM - 5:00 PM"},
                {"room": "PGN-105", "days": "Monday-Friday", "time": "7:00 AM - 9:00 PM"},
            ),
        )
    def test_admin_staff_update_rejects_operational_profile_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported account update field"):
            account_service.update_staff_account_service(
                5,
                {"consultation_rooms": ["SJH-206"]},
            )

    def test_staff_search_returns_only_authorized_public_fields(self) -> None:
        profile = {"id": 4, "assigned_programs": '["BS Computer Science"]'}
        results = [
            {
                "full_name": "Student One",
                "student_number": "2026-00001",
                "program": "BS Computer Science",
                "email": "student@example.test",
            }
        ]
        with patch.object(account_service, "fetch_account_by_id", return_value=profile), patch.object(
            account_service,
            "search_student_accounts_by_programs",
            return_value=results,
        ) as search:
            returned = account_service.search_students_for_staff_service({"id": 4}, "student")

        self.assertEqual(returned, results)
        search.assert_called_once_with("student", ("BS Computer Science",))
        self.assertNotIn("id", returned[0])

    def test_staff_self_profile_uses_session_identity_only(self) -> None:
        existing = {
            "id": 9,
            "office": "",
            "support_statement": "",
            "consultation_rooms": "[]",
            "consultation_schedules": "[]",
            "appointment_slots": "[]",
            "consultation_modes": "[]",
        }
        updated = {
            **existing,
            "office": "SJH-206",
            "consultation_rooms": '["SJH-206"]',
            "consultation_schedules": '[{"room":"SJH-206","days":"Monday","time":"09:00 AM - 05:00 PM"}]',
            "appointment_slots": '["09:00 AM","10:00 AM"]',
            "consultation_modes": '["Online","Onsite"]',
        }
        with patch.object(account_service, "fetch_account_by_id", side_effect=[existing, updated]), patch.object(
            account_service,
            "_update_account_fields_with_duplicate_email_translation",
            return_value=updated,
        ) as update:
            profile = account_service.update_own_staff_operational_profile_service(
                {"id": 9},
                {
                    "office": "SJH-206",
                    "consultation_rooms": ["SJH-206"],
                    "consultation_schedules": [
                        {"room": "SJH-206", "days": "Monday", "time": "09:00 AM - 05:00 PM"}
                    ],
                    "appointment_slots": ["10:00 AM", "9:00 AM"],
                    "consultation_modes": ["Online", "Onsite"],
                },
            )

        self.assertEqual(profile["office"], "SJH-206")
        self.assertEqual(profile["appointment_slots"], ["09:00 AM", "10:00 AM"])
        self.assertEqual(profile["consultation_modes"], ["Online", "Onsite"])
        self.assertEqual(update.call_args.args[0], 9)

    def test_staff_can_update_only_their_own_password_after_verification(self) -> None:
        credentials = {
            "id": 9,
            "status": "active",
            "password_hash": account_service.generate_password_hash("current-password"),
        }
        with patch.object(
            account_service,
            "fetch_account_password_credentials",
            return_value=credentials,
        ), patch.object(
            account_service,
            "update_account_password_hash",
            return_value=True,
        ) as update:
            account_service.update_own_staff_password_service(
                {"id": 9},
                {
                    "current_password": "current-password",
                    "new_password": "new-password",
                    "confirm_password": "new-password",
                },
            )

        self.assertEqual(update.call_args.args[0], 9)
        self.assertEqual(update.call_args.kwargs["role"], "staff")
        self.assertTrue(
            account_service.check_password_hash(
                update.call_args.args[1],
                "new-password",
            )
        )

    def test_staff_password_update_rejects_invalid_current_or_confirmation(self) -> None:
        credentials = {
            "id": 9,
            "status": "active",
            "password_hash": account_service.generate_password_hash("current-password"),
        }
        with patch.object(
            account_service,
            "fetch_account_password_credentials",
            return_value=credentials,
        ), self.assertRaisesRegex(PermissionError, "Current password is incorrect"):
            account_service.update_own_staff_password_service(
                {"id": 9},
                {
                    "current_password": "incorrect-password",
                    "new_password": "new-password",
                    "confirm_password": "new-password",
                },
            )

        with self.assertRaisesRegex(ValueError, "New passwords do not match"):
            account_service.update_own_staff_password_service(
                {"id": 9},
                {
                    "current_password": "current-password",
                    "new_password": "new-password",
                    "confirm_password": "different-password",
                },
            )

    def test_program_and_profile_routes_enforce_role_boundaries(self) -> None:
        from backend.server.routes.account_routes import account_bp
        from backend.server.routes import account_routes

        app = Flask(__name__)
        app.secret_key = "account-boundary-routes"
        app.register_blueprint(account_bp)

        def client_for(role):  # type: ignore[no-untyped-def]
            client = app.test_client()
            with client.session_transaction() as session:
                session["hau_user"] = {
                    "id": 7,
                    "email": f"{role}@example.test",
                    "role": role,
                }
            return client

        profile = {
            "office": "SJH-206",
            "support_statement": "",
            "consultation_rooms": ["SJH-206"],
            "consultation_schedules": [],
        }
        with patch.object(
            account_routes.program_service,
            "list_programs",
            return_value=[],
        ), patch.object(
            account_routes,
            "get_own_staff_operational_profile_service",
            return_value=profile,
        ):
            self.assertEqual(client_for("admin").get("/api/accounts/programs").status_code, 200)
            self.assertEqual(client_for("staff").get("/api/accounts/staff/profile").status_code, 200)

        self.assertEqual(client_for("staff").get("/api/accounts/programs").status_code, 403)
        self.assertEqual(client_for("admin").get("/api/accounts/staff/profile").status_code, 403)
        self.assertEqual(client_for("student").get("/api/accounts/programs").status_code, 403)
