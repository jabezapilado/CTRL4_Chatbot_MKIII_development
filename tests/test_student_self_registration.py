"""Regression coverage for the temporary student survey registration flow."""

from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import patch


class StudentSelfRegistrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self._environment = patch.dict(
            os.environ,
            {
                "CHATBOT_SESSION_TYPE": "cachelib",
                "CHATBOT_SESSION_FILE_DIR": self._temporary_directory.name,
                "CHATBOT_DATABASE_INITIALIZE_ON_START": "false",
                "CHATBOT_STUDENT_SELF_REGISTRATION_ENABLED": "true",
                "CHATBOT_STUDENT_SELF_REGISTRATION_CODE": "survey-code",
            },
            clear=False,
        )
        self._environment.start()
        from backend.server import create_app

        with patch("backend.server.initialize_database"):
            self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self._environment.stop()
        self._temporary_directory.cleanup()

    def _csrf_headers(self) -> dict[str, str]:
        self.client.get("/register")
        with self.client.session_transaction() as browser_session:
            return {"X-CSRF-Token": browser_session["_csrf_token"]}

    @staticmethod
    def _payload(**overrides: object) -> dict[str, object]:
        payload = {
            "full_name": "Survey Student",
            "email": "survey@student.hau.edu.ph",
            "gender": "Prefer not to say",
            "program": "BS Computer Science",
            "password": "SurveyPass123!",
            "registration_code": "survey-code",
        }
        payload.update(overrides)
        return payload

    def test_registration_page_and_api_are_disabled_without_both_configuration_values(self) -> None:
        self.app.config["STUDENT_SELF_REGISTRATION_ENABLED"] = False
        self.assertEqual(self.client.get("/register").status_code, 404)
        self.assertEqual(
            self.client.get("/auth/student-registration/programs").status_code,
            404,
        )

    def test_registration_requires_csrf_before_any_account_creation(self) -> None:
        with patch("backend.server.auth.create_student_self_registration_service") as create:
            response = self.client.post(
                "/auth/student-registration",
                json=self._payload(),
            )
        self.assertEqual(response.status_code, 403)
        create.assert_not_called()

    def test_registration_creates_only_student_with_validated_payload(self) -> None:
        created = {"id": 22, "student_number": "2024-00022"}
        with patch(
            "backend.server.auth.create_student_self_registration_service",
            return_value=created,
        ) as create:
            response = self.client.post(
                "/auth/student-registration",
                json=self._payload(),
                headers=self._csrf_headers(),
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["data"], {"student_number": "2024-00022"})
        create.assert_called_once()
        self.assertEqual(create.call_args.kwargs["registration_code"], "survey-code")

    def test_service_rejects_wrong_code_non_student_email_and_role_injection(self) -> None:
        from backend.server.services.account_service import (
            create_student_self_registration_service,
        )

        with self.assertRaisesRegex(PermissionError, "registration code"):
            create_student_self_registration_service(
                self._payload(registration_code="wrong"),
                registration_code="survey-code",
            )
        with self.assertRaisesRegex(ValueError, "school student email"):
            create_student_self_registration_service(
                self._payload(email="staff@hau.edu.ph"),
                registration_code="survey-code",
            )
        with self.assertRaisesRegex(ValueError, "Unsupported registration field"):
            create_student_self_registration_service(
                self._payload(role="admin"),
                registration_code="survey-code",
            )


if __name__ == "__main__":
    unittest.main()
