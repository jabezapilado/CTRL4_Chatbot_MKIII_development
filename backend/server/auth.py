from __future__ import annotations

from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash

from .db import fetch_account_by_email


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    account = fetch_account_by_email(email)
    if not account:
        return jsonify({"error": "Invalid credentials."}), 401

    if account["status"] != "active":
        return jsonify({"error": "Account is disabled."}), 403

    stored_password = str(account.get("password_hash", ""))
    password_ok = False

    # Support modern hashed credentials and legacy plaintext seeds.
    if stored_password.startswith(("pbkdf2:", "scrypt:")):
        password_ok = check_password_hash(stored_password, password)
    else:
        password_ok = password == stored_password

    if not password_ok:
        return jsonify({"error": "Invalid credentials."}), 401

    session["hau_user"] = {
        "id": account["id"],
        "student_number": account.get("student_number"),
        "email": account["email"],
        "full_name": account["full_name"],
        "role": account["role"],
    }

    return jsonify(
        {
            "id": account["id"],
            "student_number": account.get("student_number"),
            "email": account["email"],
            "full_name": account["full_name"],
            "role": account["role"],
        }
    ), 200


@auth_bp.post("/auth/logout")
def logout():
    session.clear()
    return jsonify({"status": "logged_out"}), 200