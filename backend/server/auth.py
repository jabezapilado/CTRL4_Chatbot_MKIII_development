from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request, session
from .services.account_service import login_service, logout_service


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
    except ValueError as exc:
        logger.warning("Login failed: %s", exc)
        return jsonify({"error": str(exc)}), 400
    except PermissionError as exc:
        logger.warning("Login denied: %s", exc)
        return jsonify({"error": str(exc)}), 401
    except RuntimeError as exc:
        logger.warning("Login blocked: %s", exc)
        return jsonify({"error": str(exc)}), 403

    logger.info(
        "User %s logged in as %s",
        user["email"],
        user.get("role", "student"),
    )
    return jsonify(user), 200


@auth_bp.post("/auth/logout")
def logout():
    user = get_logged_in_user()
    logout_service()
    if user:
        logger.info("User %s logged out", user["email"])
    return jsonify({"status": "logged_out"}), 200