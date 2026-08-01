from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request, session
from .services.account_service import login_service
from .request_validation import require_login


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

@auth_bp.post("/auth/login")
def login():
    payload = request.get_json(silent=True) or {}

    try:
        user = login_service(payload)
        # Prevent session fixation by issuing a fresh authenticated session.
        session.clear()
        session.permanent = True
        session["hau_user"] = user
    except ValueError as exc:
        logger.warning("Login failed: %s", exc)
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400
    except PermissionError as exc:
        logger.warning("Login denied: %s", exc)
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 401
    except RuntimeError as exc:
        logger.warning("Login blocked: %s", exc)
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 403

    logger.info(
        "User %s logged in as %s",
        user["email"],
        user.get("role", "student"),
    )
    return jsonify(
        {
            "success": True,
            "message": "Logged in successfully.",
            "data": user,
        }
    ), 200


@auth_bp.post("/auth/logout")
def logout():
    user = require_login()
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
        logger.info("User %s logged out", user["email"])
    return jsonify(
        {
            "success": True,
            "message": "Logged out successfully.",
            "data": None,
        }
    ), 200
