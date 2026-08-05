"""Deployment-contract checks that do not require a database or AI provider."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DeploymentConfigurationTests(unittest.TestCase):
    def _production_environment(self, session_directory: str, log_file: str) -> dict[str, str]:
        return {
            "CHATBOT_ENV": "production",
            "CHATBOT_DEBUG": "false",
            "CHATBOT_SECRET_KEY": "deployment-test-secret-not-a-default",
            "CHATBOT_SESSION_COOKIE_SECURE": "true",
            "CHATBOT_SESSION_FILE_DIR": session_directory,
            "CHATBOT_LOG_FILE": log_file,
            "CHATBOT_DATABASE_INITIALIZE_ON_START": "false",
            "CHATBOT_DATABASE_BACKUP_CONFIRMED": "false",
        }

    def test_development_defaults_preserve_existing_startup_behavior(self) -> None:
        from backend.server.config import Config

        with patch.dict(
            os.environ,
            {
                "CHATBOT_ENV": "development",
                "CHATBOT_DEBUG": "true",
                "CHATBOT_DATABASE_INITIALIZE_ON_START": "true",
            },
            clear=False,
        ):
            config = Config()

        self.assertFalse(config.IS_PRODUCTION)
        self.assertTrue(config.DEBUG)
        self.assertTrue(config.DATABASE_INITIALIZE_ON_START)

    def test_production_configuration_requires_explicit_safe_values(self) -> None:
        from backend.server.config import Config

        with tempfile.TemporaryDirectory() as temporary_directory:
            environment = self._production_environment(
                temporary_directory,
                str(Path(temporary_directory) / "ctrl4.log"),
            )
            with patch.dict(os.environ, environment, clear=False):
                config = Config()

        self.assertTrue(config.IS_PRODUCTION)
        self.assertFalse(config.DEBUG)
        self.assertTrue(config.SESSION_COOKIE_SECURE)
        self.assertFalse(config.DATABASE_INITIALIZE_ON_START)

    def test_production_configuration_rejects_unsafe_startup(self) -> None:
        from backend.server.config import Config

        with patch.dict(
            os.environ,
            {
                "CHATBOT_ENV": "production",
                "CHATBOT_DEBUG": "true",
                "CHATBOT_SECRET_KEY": "dev-secret-key-change-me",
                "CHATBOT_SESSION_COOKIE_SECURE": "false",
                "CHATBOT_SESSION_FILE_DIR": "",
                "CHATBOT_LOG_FILE": "",
                "CHATBOT_DATABASE_INITIALIZE_ON_START": "true",
                "CHATBOT_DATABASE_BACKUP_CONFIRMED": "false",
            },
            clear=False,
        ):
            with self.assertRaises(RuntimeError) as raised:
                Config()

        self.assertIn("CHATBOT_DEBUG", str(raised.exception))
        self.assertIn("CHATBOT_DATABASE_BACKUP_CONFIRMED", str(raised.exception))
        self.assertIn("CHATBOT_LOG_FILE", str(raised.exception))

    def test_requirements_have_one_authoritative_source(self) -> None:
        root_requirements = (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8")
        backend_requirements = (PROJECT_ROOT / "backend/requirements.txt").read_text(encoding="utf-8")

        self.assertIn("google-generativeai", root_requirements)
        self.assertIn("requests", root_requirements)
        self.assertIn("gunicorn", root_requirements)
        self.assertEqual(backend_requirements.strip().splitlines()[-1], "-r ../requirements.txt")

    def test_fresh_schema_does_not_hard_code_a_database_name(self) -> None:
        schema = (PROJECT_ROOT / "backend/sql/schema.sql").read_text(encoding="utf-8")

        self.assertNotIn("CREATE DATABASE IF NOT EXISTS soc_chatbot", schema)
        self.assertNotIn("USE soc_chatbot", schema)

    def test_deployment_scripts_are_safe_shell_syntax(self) -> None:
        for script in (
            "backend/scripts/backup_database.sh",
            "backend/scripts/restore_database.sh",
        ):
            with self.subTest(script=script):
                result = subprocess.run(
                    ["bash", "-n", str(PROJECT_ROOT / script)],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_deployment_setup_logging_is_aggregate_only(self) -> None:
        setup_script = (PROJECT_ROOT / "backend/scripts/setup_database.py").read_text(
            encoding="utf-8"
        )
        auth = (PROJECT_ROOT / "backend/server/auth.py").read_text(encoding="utf-8")

        self.assertNotIn('account["email"]', setup_script)
        self.assertNotIn('user["email"]', auth)


if __name__ == "__main__":
    unittest.main()
