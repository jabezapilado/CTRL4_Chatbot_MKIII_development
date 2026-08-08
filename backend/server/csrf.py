"""CSRF protection for browser requests authenticated by server-side sessions."""

from __future__ import annotations

import hmac
import secrets

from flask import Flask, jsonify, request, session


CSRF_SESSION_KEY = "_csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


def get_csrf_token() -> str:
    """Return the opaque token bound to the current server-side session."""
    token = session.get(CSRF_SESSION_KEY)
    if isinstance(token, str) and token:
        return token

    token = secrets.token_urlsafe(32)
    session[CSRF_SESSION_KEY] = token
    return token


def _has_authenticated_session() -> bool:
    user = session.get("hau_user")
    return isinstance(user, dict) and bool(user.get("email"))


def install_csrf_protection(app: Flask) -> None:
    @app.context_processor
    def inject_csrf_token() -> dict[str, str]:
        return {"csrf_token": get_csrf_token()}

    @app.before_request
    def validate_csrf_token():
        if request.method in SAFE_METHODS:
            return None

        # Login starts without an authenticated session, but its page bootstrap
        # token still protects the session-establishing request. Other expired
        # sessions continue to the existing route guard and return its 401.
        if request.endpoint != "auth.login" and not _has_authenticated_session():
            return None

        expected = session.get(CSRF_SESSION_KEY)
        provided = request.headers.get(CSRF_HEADER_NAME, "")
        if isinstance(expected, str) and hmac.compare_digest(expected, provided):
            return None

        return jsonify(
            {
                "success": False,
                "message": "CSRF validation failed.",
                "errors": None,
            }
        ), 403
