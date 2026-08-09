"""Dependency-free release-gate checks for Issue #75."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class ReleaseGateContractTests(unittest.TestCase):
    def test_admin_landing_uses_the_authorized_account_page(self) -> None:
        from backend.server.auth import role_landing_path

        self.assertEqual(role_landing_path({"role": "admin"}), "/admin")

        frontend_routes = _read("backend/server/routes/frontend_routes.py")
        self.assertIn('@frontend_bp.get("/admin")', frontend_routes)
        self.assertIn('return render_template(\n        "admin.html",', frontend_routes)
        self.assertIn('if path == "/admin" and role != ROLE_ADMIN:', frontend_routes)
        self.assertIn('if path == "/dashboard" and role == ROLE_ADMIN:', frontend_routes)
        self.assertIn(
            'redirectToPage("/admin")',
            _read("frontend/templates/login.html"),
        )

    def test_dashboard_has_no_calls_to_unregistered_legacy_mutations(self) -> None:
        dashboard = _read("frontend/static/js/dashboard.js")

        self.assertNotIn('fetchJson(`${API_BASE}/api/inquiries`,', dashboard)
        self.assertNotIn('/api/conversation-summaries/${', dashboard)
        self.assertNotIn('view-manual-entry', _read("frontend/templates/dashboard.html"))

    def test_current_readme_and_documents_use_mk_iii_branding(self) -> None:
        current_documents = (
            "README.md",
            "requirements.txt",
            "docs/architecture/project_architecture.md",
            "docs/deployment/deployment_guide.md",
            "docs/architecture/security_architecture.md",
            "docs/architecture/api_reference.md",
            "docs/deployment/installation_guide.md",
            "docs/guides/student_guide.md",
            "docs/guides/guidance_staff_guide.md",
            "docs/guides/administrator_guide.md",
            "docs/architecture/project_context.md",
            "backend/server/services/__init__.py",
        )

        for path in current_documents:
            with self.subTest(path=path):
                self.assertNotRegex(
                    _read(path),
                    r"CTRL4 Chatbot MK II(?!I)",
                )

        readme = _read("README.md")
        self.assertIn("CTRL4 Chatbot MK III", readme)
        self.assertIn("v1.0.7", readme)
        self.assertIn("docs/README.md", readme)
        self.assertIn("http://127.0.0.1:5001", readme)
        self.assertNotIn("student123", readme)

    def test_historical_documents_are_archived_without_rewriting_them(self) -> None:
        archived = (
            "02_dataset_documentation.md",
            "03_preprocessing_pipeline.md",
            "04_model_architecture.md",
            "05_api_integration.md",
            "07_future_work.md",
            "08_design_decisions.md",
            "09_ethical_legal_and_privacy.md",
            "CTRL4_BIBLE.md",
            "sprint3_account_management_audit.md",
        )

        for name in archived:
            with self.subTest(name=name):
                self.assertFalse((ROOT / "docs" / name).exists())
                self.assertTrue((ROOT / "docs" / "archive" / name).exists())

        self.assertIn(
            "Historical Documentation Archive",
            _read("docs/archive/README.md"),
        )

    def test_active_templates_reference_existing_static_assets(self) -> None:
        static_root = ROOT / "frontend" / "static"
        pattern = re.compile(r'(?:src|href)="/static/([^"]+)"')

        for template in (ROOT / "frontend" / "templates").glob("*.html"):
            source = template.read_text(encoding="utf-8")
            for asset in pattern.findall(source):
                with self.subTest(template=template.name, asset=asset):
                    self.assertTrue((static_root / asset).is_file())


if __name__ == "__main__":
    unittest.main()
