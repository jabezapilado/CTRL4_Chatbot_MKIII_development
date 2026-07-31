from werkzeug.security import generate_password_hash

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
