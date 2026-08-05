from __future__ import annotations

import logging

from flask import Blueprint, current_app, jsonify, request, session
from .services.account_service import login_service


logger = logging.getLogger(__name__)


auth_bp = Blueprint("auth", __name__)


def get_logged_in_user() -> dict | None:
    user = session.get("hau_user")
    return user if isinstance(user, dict) and user.get("email") else None


def role_landing_path(user: dict) -> str:
    role = str(user.get("role", "student")).lower()

    if role == "staff":
        return "/dashboard"

    if role == "admin":
        return "/admin"

    return "/chatbot"


def _rotate_authenticated_session() -> None:
    """Replace the server-side session identifier after successful login."""
    regenerate = getattr(current_app.session_interface, "regenerate", None)
    if callable(regenerate):
        regenerate(session)

@auth_bp.post("/auth/login")
def login():
    payload = request.get_json(silent=True) or {}

    try:
        user = login_service(payload)
        # Prevent session fixation by issuing a fresh authenticated session.
        session.clear()
        session["hau_user"] = user
        _rotate_authenticated_session()
        session.permanent = True
    except ValueError as exc:
        logger.warning("Login validation failed.")
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400
    except PermissionError as exc:
        logger.warning("Login denied.")
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 401
    except RuntimeError as exc:
        logger.warning("Login blocked.")
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 403

    logger.info("Authenticated session established (role=%s).", user.get("role", "student"))
    return jsonify(
        {
            "success": True,
            "message": "Logged in successfully.",
            "data": user,
        }
    ), 200


@auth_bp.post("/auth/logout")
def logout():
    user = get_logged_in_user()
    if not user:
        return jsonify(
            {
                "success": False,
                "message": "Login required.",
                "errors": None,
            }
        ), 401
    session.clear()
    if user:
        logger.info("Authenticated session cleared.")
    return jsonify(
        {
            "success": True,
            "message": "Logged out successfully.",
            "data": None,
        }
    ), 200
