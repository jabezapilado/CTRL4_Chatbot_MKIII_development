"""Dependency-free regression checks for login redirect stability."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path

from flask import Flask, session


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _load_frontend_blueprint_for_test():
    """Load only the frontend route module without starting the AI services."""

    package_paths = {
        "backend": ROOT / "backend",
        "backend.server": ROOT / "backend" / "server",
        "backend.server.routes": ROOT / "backend" / "server" / "routes",
    }
    for name, path in package_paths.items():
        package = types.ModuleType(name)
        package.__path__ = [str(path)]
        sys.modules[name] = package

    auth = types.ModuleType("backend.server.auth")
    auth.get_logged_in_user = lambda: (
        session.get("hau_user")
        if isinstance(session.get("hau_user"), dict)
        and session.get("hau_user", {}).get("email")
        else None
    )
    auth.role_landing_path = lambda user: {
        "staff": "/dashboard",
        "admin": "/admin",
    }.get(str(user.get("role", "student")).lower(), "/chatbot")
    auth.STUDENT_TERMS_ACCEPTED_SESSION_KEY = "student_terms_accepted"
    sys.modules["backend.server.auth"] = auth

    validation = types.ModuleType("backend.server.request_validation")
    validation.ROLE_STUDENT = "student"
    validation.ROLE_STAFF = "staff"
    validation.ROLE_ADMIN = "admin"
    sys.modules["backend.server.request_validation"] = validation

    module_name = "backend.server.routes._frontend_routes_contract"
    spec = importlib.util.spec_from_file_location(
        module_name,
        ROOT / "backend" / "server" / "routes" / "frontend_routes.py",
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load frontend route contract module.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.frontend_bp


class LoginRedirectContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        app = Flask(
            "login-redirect-contract",
            template_folder=str(ROOT / "frontend" / "templates"),
        )
        app.secret_key = "login-redirect-contract-secret"
        app.register_blueprint(_load_frontend_blueprint_for_test())
        cls.app = app

    def _client_for(self, role: str | None = None):
        client = self.app.test_client()
        if role:
            with client.session_transaction() as client_session:
                client_session["hau_user"] = {
                    "email": f"{role}@example.test",
                    "role": role,
                }
        return client

    def test_login_page_does_not_redirect_using_stale_browser_identity(self) -> None:
        login = _read("frontend/templates/login.html")

        self.assertIn('sessionStorage.removeItem("hau_user")', login)
        self.assertNotIn('sessionStorage.getItem("hau_user")', login)
        self.assertNotIn("/auth/me", login)
        self.assertEqual(login.count("showLoginNotice();"), 1)
        self.assertIn("showLoginNotice();", login)

    def test_unauthenticated_login_routes_remain_stable(self) -> None:
        for path in ("/login", "/login?reason=session-required"):
            with self.subTest(path=path):
                response = self._client_for().get(path, follow_redirects=False)
                self.assertEqual(response.status_code, 200)
                self.assertNotIn("Location", response.headers)

    def test_protected_route_redirects_to_login_once(self) -> None:
        response = self._client_for().get("/dashboard", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.history), 1)
        self.assertEqual(
            response.history[0].headers["Location"],
            "/login?reason=session-required",
        )

    def test_authenticated_roles_land_on_valid_server_authorized_pages(self) -> None:
        expected_paths = {
            "student": "/chatbot",
            "staff": "/dashboard",
            "admin": "/admin",
        }
        for role, expected_path in expected_paths.items():
            with self.subTest(role=role):
                response = self._client_for(role).get("/login", follow_redirects=False)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.headers["Location"], expected_path)

    def test_administrator_portal_is_available_only_to_administrators(self) -> None:
        for role, expected_status, expected_location in (
            ("student", 302, "/chatbot"),
            ("staff", 302, "/dashboard"),
            ("admin", 200, None),
        ):
            with self.subTest(role=role):
                response = self._client_for(role).get("/admin", follow_redirects=False)
                self.assertEqual(response.status_code, expected_status)
                if expected_location:
                    self.assertEqual(response.headers["Location"], expected_location)
                else:
                    self.assertIn(b"Account Management", response.data)
                    self.assertIn(b'id="admin-programs"', response.data)

    def test_invalid_session_payload_remains_on_login(self) -> None:
        client = self._client_for()
        with client.session_transaction() as client_session:
            client_session["hau_user"] = "expired-or-invalid"

        response = client.get("/login", follow_redirects=False)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Location", response.headers)

    def test_session_required_login_notice_is_presentation_only(self) -> None:
        login = _read("frontend/templates/login.html")
        notice_start = login.index("function showLoginNotice()")
        notice_end = login.index("showLoginNotice();", notice_start)
        notice_source = login[notice_start:notice_end]

        self.assertIn('reason === "session-required"', notice_source)
        self.assertIn('reason === "session-replaced"', notice_source)
        self.assertNotIn("redirectToPage", notice_source)
        self.assertNotIn("window.location.replace", notice_source)

    def test_server_route_is_the_authority_for_login_and_role_landings(self) -> None:
        routes = _read("backend/server/routes/frontend_routes.py")
        auth = _read("backend/server/auth.py")

        self.assertIn('public_paths = {"/", "/login", "/health", "/auth/login", "/auth/logout"}', routes)
        self.assertIn('if path in {"/", "/login"} and user:', routes)
        self.assertIn('def _login_redirect_for_current_session_state()', routes)
        self.assertIn('"session-replaced"', routes)
        self.assertIn('if role == "staff":\n        return "/dashboard"', auth)
        self.assertIn('if role == "admin":\n        return "/admin"', auth)
        self.assertIn('return "/chatbot"', auth)

    def test_login_and_logout_navigation_remain_single_and_explicit(self) -> None:
        login = _read("frontend/templates/login.html")
        client_auth = _read("frontend/static/js/auth.js")

        self.assertIn('redirectToPage("/dashboard")', login)
        self.assertIn('redirectToPage("/admin")', login)
        self.assertIn('redirectToPage("/chatbot")', login)
        self.assertEqual(
            client_auth.count(
                "window.location.replace(`/login?reason=${encodeURIComponent(reason)}`)",
            ),
            1,
        )
        self.assertIn("sessionStorage.clear()", client_auth)


if __name__ == "__main__":
    unittest.main()
