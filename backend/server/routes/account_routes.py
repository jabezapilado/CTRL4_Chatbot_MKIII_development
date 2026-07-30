from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from ..auth import get_logged_in_user

from ..db import (
    list_accounts,
    search_student_accounts,
    create_account,
    fetch_account_by_email,
)

account_bp = Blueprint(
    "accounts",
    __name__,
    url_prefix="/api/accounts",
)

@account_bp.get("")
def accounts():
    return jsonify({"items": list_accounts()}), 200


@account_bp.get("/search")
def search_accounts():
    user = get_logged_in_user()

    if not user or str(user.get("role", "")).lower() != "staff":
        return jsonify({"error": "Staff access required."}), 403

    query = str(request.args.get("q", "")).strip()

    if not query:
        return jsonify({"items": []}), 200

    return jsonify(
        {
            "items": search_student_accounts(query)
        }
    ), 200


@account_bp.post("")
def create_account_route():
    user = get_logged_in_user()

    if not user or str(user.get("role", "")).lower() != "admin":
        return jsonify({"error": "Administrator access required."}), 403

    payload = request.get_json(silent=True) or {}

    full_name = str(payload.get("full_name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    role = str(payload.get("role", "student")).strip().lower()

    gender = str(payload.get("gender", "")).strip() or None
    program = str(payload.get("program", "")).strip() or None

    if not full_name or not email or not password:
        return jsonify({"error": "Missing required fields."}), 400

    if fetch_account_by_email(email):
        return jsonify({"error": "Email already exists."}), 409

    if role == "student":
        if not program:
            return jsonify({"error": "Program is required."}), 400
        if not gender:
            return jsonify({"error": "Gender is required."}), 400

    elif role in {"staff", "admin"}:
        if not gender:
            return jsonify({"error": "Gender is required."}), 400

    else:
        return jsonify({"error": "Invalid account role."}), 400

    account = create_account(
        full_name=full_name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        student_number=None,
        staff_number=None,
        gender=gender,
        program=program,
    )

    return jsonify(
        {
            "id": account["id"],
            "status": "created",
            "student_number": account["student_number"],
            "staff_number": account["staff_number"],
        }
    ), 201