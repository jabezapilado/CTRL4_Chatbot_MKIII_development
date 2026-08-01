from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

import re

from ..db import (
    create_account,
    fetch_account_by_email,
)

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Centralized valid roles
VALID_ROLES = frozenset({"student", "staff", "admin"})


def create_account_service(payload: dict) -> dict:
    full_name = str(payload.get("full_name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    role = str(payload.get("role", "student")).strip().lower()

    gender = str(payload.get("gender", "")).strip() or None
    program = str(payload.get("program", "")).strip() or None

    if not full_name or not email or not password:
        raise ValueError("Missing required fields.")

    if not password.strip():
        raise ValueError("Password cannot be blank.")

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not EMAIL_PATTERN.fullmatch(email):
        raise ValueError("Invalid email address.")

    if fetch_account_by_email(email):
        raise FileExistsError("Email already exists.")

    if role == "student":
        if not program:
            raise ValueError("Program is required.")
        if not gender:
            raise ValueError("Gender is required.")
    elif role in VALID_ROLES - {"student"}:
        if not gender:
            raise ValueError("Gender is required.")
    elif role not in VALID_ROLES:
        raise ValueError("Invalid account role.")

    return create_account(
        full_name=full_name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        student_number=None,
        staff_number=None,
        gender=gender,
        program=program,
    )


def login_service(payload: dict) -> dict:
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))

    if not email or not password:
        raise ValueError("Email and password are required.")
    if not EMAIL_PATTERN.fullmatch(email):
        raise ValueError("Invalid email address.")

    account = fetch_account_by_email(email)
    if not account:
        raise PermissionError("Invalid credentials.")

    if account.get("status") != "active":
        raise PermissionError("Invalid credentials.")

    role = str(account.get("role", "")).strip().lower()
    if role not in VALID_ROLES:
        raise PermissionError("Invalid account configuration.")

    stored_password = str(account.get("password_hash", ""))
    # All accounts are stored using Werkzeug password hashes.
    # Legacy plaintext password support has been removed.
    password_ok = check_password_hash(stored_password, password)

    if not password_ok:
        raise PermissionError("Invalid credentials.")

    user = {
        "id": account["id"],
        "student_number": account.get("student_number"),
        "email": account["email"],
        "full_name": account["full_name"],
        "role": role,
    }

    session["hau_user"] = user
    return user


def logout_service() -> None:
    session.clear()
