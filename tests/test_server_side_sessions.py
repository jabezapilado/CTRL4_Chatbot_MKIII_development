"""Focused runtime checks for the configured Flask-Session behavior.

These tests deliberately use a temporary filesystem backend rather than the
project MySQL database. They validate the session primitive used by the app
without creating or altering application data.
"""

from __future__ import annotations

import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from cachelib.file import FileSystemCache
from flask import Flask, jsonify, session
from flask_session import Session


class ServerSideSessionTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret-key",
            SESSION_TYPE="cachelib",
            SESSION_CACHELIB=FileSystemCache(
                cache_dir=self._temporary_directory.name,
                threshold=50,
                mode=0o700,
            ),
            SESSION_PERMANENT=True,
            SESSION_COOKIE_NAME="ctrl4_test_session",
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_SAMESITE="Lax",
            PERMANENT_SESSION_LIFETIME=timedelta(minutes=5),
        )
        Session(self.app)

        @self.app.post("/pre-auth")
        def pre_auth():
            session["pre_auth"] = True
            return jsonify({"success": True})

        @self.app.post("/login")
        def login():
            session.clear()
            session["hau_user"] = {"id": 1, "role": "student"}
            self.app.session_interface.regenerate(session)
            session.permanent = True
            return jsonify({"success": True})

        @self.app.get("/protected")
        def protected():
            if "hau_user" not in session:
                return jsonify({"success": False}), 401
            return jsonify({"success": True})

        @self.app.get("/staff-only")
        def staff_only():
            user = session.get("hau_user")
            if not user:
                return jsonify({"success": False}), 401
            if user.get("role") != "staff":
                return jsonify({"success": False}), 403
            return jsonify({"success": True})

        @self.app.post("/logout")
        def logout():
            session.clear()
            return jsonify({"success": True})

        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def _session_cookie(self) -> str:
        cookie = self.client.get_cookie("ctrl4_test_session")
        self.assertIsNotNone(cookie)
        return cookie.value

    def test_cookie_is_opaque_rotated_and_has_security_attributes(self) -> None:
        initial_response = self.client.post("/pre-auth")
        initial_cookie = self._session_cookie()

        login_response = self.client.post("/login")
        rotated_cookie = self._session_cookie()
        set_cookie = login_response.headers.get("Set-Cookie", "")

        self.assertEqual(initial_response.status_code, 200)
        self.assertEqual(login_response.status_code, 200)
        self.assertNotEqual(initial_cookie, rotated_cookie)
        self.assertNotIn("hau_user", rotated_cookie)
        self.assertNotIn("pre_auth", rotated_cookie)
        self.assertIn("HttpOnly", set_cookie)
        self.assertIn("Secure", set_cookie)
        self.assertIn("SameSite=Lax", set_cookie)
        self.assertIn("Expires=", set_cookie)
        self.assertGreater(len(list(Path(self._temporary_directory.name).iterdir())), 0)

    def test_authenticated_requests_logout_invalidation_and_rbac(self) -> None:
        self.client.post("/login")
        session_id = self._session_cookie()

        self.assertEqual(self.client.get("/protected").status_code, 200)
        self.assertEqual(self.client.get("/staff-only").status_code, 403)
        self.assertEqual(self.client.post("/logout").status_code, 200)
        self.assertEqual(self.client.get("/protected").status_code, 401)

        invalid_client = self.app.test_client()
        invalid_client.set_cookie("ctrl4_test_session", session_id)
        self.assertEqual(invalid_client.get("/protected").status_code, 401)


if __name__ == "__main__":
    unittest.main()
