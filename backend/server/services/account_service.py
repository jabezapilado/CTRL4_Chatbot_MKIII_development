from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

from ..db import (
    create_account,
    fetch_account_by_email,
)


def create_account_service(payload: dict) -> dict:
    full_name = str(payload.get("full_name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    role = str(payload.get("role", "student")).strip().lower()

    gender = str(payload.get("gender", "")).strip() or None
    program = str(payload.get("program", "")).strip() or None

    if not full_name or not email or not password:
        raise ValueError("Missing required fields.")

    if fetch_account_by_email(email):
        raise FileExistsError("Email already exists.")

    if role == "student":
        if not program:
            raise ValueError("Program is required.")
        if not gender:
            raise ValueError("Gender is required.")
    elif role in {"staff", "admin"}:
        if not gender:
            raise ValueError("Gender is required.")
    else:
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

    account = fetch_account_by_email(email)
    if not account:
        raise PermissionError("Invalid credentials.")

    if account["status"] != "active":
        raise RuntimeError("Account is disabled.")

    stored_password = str(account.get("password_hash", ""))
    if stored_password.startswith(("pbkdf2:", "scrypt:")):
        password_ok = check_password_hash(stored_password, password)
    else:
        password_ok = password == stored_password

    if not password_ok:
        raise PermissionError("Invalid credentials.")

    user = {
        "id": account["id"],
        "student_number": account.get("student_number"),
        "email": account["email"],
        "full_name": account["full_name"],
        "role": account["role"],
    }

    session["hau_user"] = user
    return user


def logout_service() -> None:
    session.clear()
