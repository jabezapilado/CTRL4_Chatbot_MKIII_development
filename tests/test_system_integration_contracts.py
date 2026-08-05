"""Dependency-free regression checks for the system integration contract.

These checks intentionally inspect only public wiring and module boundaries.  The
database-backed Flask suite lives in ``test_system_integration_runtime.py`` and
is opt-in because it requires an explicitly configured isolated MySQL database.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _source(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


class SystemIntegrationContractTests(unittest.TestCase):
    def test_all_system_blueprints_are_registered(self) -> None:
        source = _source("backend/server/routes/__init__.py")

        for blueprint in (
            "auth_bp",
            "appointment_bp",
            "chatbot_bp",
            "dashboard_bp",
            "conversation_bp",
            "notification_bp",
            "frontend_bp",
        ):
            self.assertIn(f"app.register_blueprint({blueprint})", source)

    def test_protected_system_routes_reuse_existing_rbac_helpers(self) -> None:
        expected_guards = {
            "backend/server/routes/appointment_routes.py": "require_role",
            "backend/server/routes/conversation_routes.py": "require_role",
            "backend/server/routes/dashboard_routes.py": "require_role",
            "backend/server/routes/notification_routes.py": "require_any_role",
            "backend/server/routes/chatbot_routes.py": "require_login",
        }

        for path, guard in expected_guards.items():
            with self.subTest(path=path):
                self.assertIn(guard, _source(path))

    def test_dashboard_analytics_remain_service_owned(self) -> None:
        source = _source("backend/server/routes/dashboard_routes.py")

        for service in (
            "get_appointment_analytics_service",
            "get_chatbot_analytics_service",
            "get_counselor_workload_analytics_service",
            "get_flagged_case_analytics_service",
        ):
            self.assertIn(service, source)

    def test_services_remain_framework_agnostic(self) -> None:
        services_directory = PROJECT_ROOT / "backend/server/services"

        for path in services_directory.glob("*.py"):
            with self.subTest(path=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                flask_imports = [
                    node
                    for node in ast.walk(tree)
                    if (
                        isinstance(node, ast.Import)
                        and any(alias.name == "flask" for alias in node.names)
                    )
                    or (
                        isinstance(node, ast.ImportFrom)
                        and node.module == "flask"
                    )
                ]
                self.assertEqual(flask_imports, [])

    def test_reports_reuses_the_existing_analytics_endpoints(self) -> None:
        source = _source("frontend/static/js/dashboard.js")

        for endpoint in (
            "/api/dashboard/appointments/analytics",
            "/api/dashboard/chatbot/analytics",
            "/api/dashboard/counselor-workload",
            "/api/dashboard/flagged-cases/analytics",
        ):
            self.assertIn(endpoint, source)


if __name__ == "__main__":
    unittest.main()
