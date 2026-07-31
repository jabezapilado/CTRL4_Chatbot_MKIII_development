from __future__ import annotations

from flask import Blueprint, jsonify, request, session
from .services.account_service import login_service, logout_service


auth_bp = Blueprint("auth", __name__)

def get_logged_in_user():
    user = session.get("hau_user")
    return user if isinstance(user, dict) and user.get("email") else None


def role_landing_path(user: dict) -> str:
    role = str(user.get("role", "student")).lower()

    if role in {"staff", "admin"}:
        return "/dashboard"

    return "/chatbot"

@auth_bp.post("/auth/login")
def login():
    payload = request.get_json(silent=True) or {}

    try:
        user = login_service(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except PermissionError as exc:
        return jsonify({"error": str(exc)}), 401
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 403

    return jsonify(user), 200


@auth_bp.post("/auth/logout")
def logout():
    logout_service()
    return jsonify({"status": "logged_out"}), 200