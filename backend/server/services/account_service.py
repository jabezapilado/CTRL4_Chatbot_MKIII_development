import json
import re

from werkzeug.security import check_password_hash, generate_password_hash

from ..db import (
    ALLOWED_ACCOUNT_ROLES,
    ALLOWED_ACCOUNT_STATUSES,
    ALLOWED_GENDERS,
    create_account,
    fetch_account_by_id,
    fetch_account_by_email,
    list_accounts,
    update_account_fields,
)
from ..config import Config

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

VALID_ROLES = ALLOWED_ACCOUNT_ROLES
ADMIN_ACCOUNT_CREATE_FIELDS = frozenset({
    "full_name",
    "email",
    "password",
    "role",
    "gender",
})
ADMIN_ACCOUNT_UPDATE_FIELDS = frozenset({
    "full_name",
    "email",
    "gender",
})
STUDENT_ACCOUNT_UPDATE_FIELDS = frozenset({
    "full_name",
    "email",
    "gender",
    "program",
})
STAFF_ACCOUNT_UPDATE_FIELDS = frozenset({
    "full_name",
    "email",
    "gender",
    "assigned_programs",
    "office",
    "support_statement",
    "consultation_rooms",
    "consultation_schedules",
})
CONSULTATION_SCHEDULE_FIELDS = frozenset({"room", "days", "time"})

config = Config()


def _validate_full_name(value: object) -> str:
    full_name = str(value or "").strip()
    if not full_name:
        raise ValueError("Full name is required.")
    return full_name


def _validate_email(value: object, *, existing_account_id: int | None = None) -> str:
    email = str(value or "").strip().lower()
    if not email:
        raise ValueError("Email is required.")
    if not EMAIL_PATTERN.fullmatch(email):
        raise ValueError("Invalid email address.")

    account_with_email = fetch_account_by_email(email)
    if (
        account_with_email
        and account_with_email["id"] != existing_account_id
    ):
        raise FileExistsError("Email already exists.")

    return email


def _validate_gender(value: object) -> str:
    gender = str(value or "").strip()
    if not gender:
        raise ValueError("Gender is required.")
    if gender not in ALLOWED_GENDERS:
        raise ValueError("Invalid gender.")
    return gender


def _validate_role(value: object) -> str:
    role = str(value).strip().lower()
    if role not in VALID_ROLES:
        raise ValueError("Invalid account role.")
    return role


def _validate_status(value: object) -> str:
    status = str(value or "").strip().lower()
    if status not in ALLOWED_ACCOUNT_STATUSES:
        raise ValueError("Invalid account status.")
    return status


def _validate_student_program(value: object) -> str:
    program = str(value or "").strip()
    if not program:
        raise ValueError("Program is required.")
    if program not in config.PROGRAMS:
        raise ValueError("Invalid program.")
    return program


def _decode_list(value: object) -> list:
    if value is None:
        return []
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return []
    return value if isinstance(value, list) else []


def _validate_program_list(value: object) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("Assigned programs must be a list.")

    programs: list[str] = []
    seen_programs: set[str] = set()
    for item in value:
        program = str(item or "").strip()
        if not program:
            raise ValueError("Assigned programs cannot contain blank values.")
        if program not in config.PROGRAMS:
            raise ValueError("Invalid assigned program.")
        if program in seen_programs:
            raise ValueError("Assigned programs cannot contain duplicates.")
        programs.append(program)
        seen_programs.add(program)

    return programs


def _validate_text_field(
    value: object,
    *,
    max_length: int | None = None,
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Account profile field must be text.")

    text = value.strip()
    if not text:
        return None
    if max_length and len(text) > max_length:
        raise ValueError("Account profile field is too long.")

    return text


def _validate_room_list(value: object) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("Consultation rooms must be a list.")

    rooms: list[str] = []
    seen_rooms: set[str] = set()
    for item in value:
        room = str(item or "").strip()
        if not room:
            raise ValueError("Consultation rooms cannot contain blank values.")
        if room in seen_rooms:
            raise ValueError("Consultation rooms cannot contain duplicates.")
        rooms.append(room)
        seen_rooms.add(room)

    return rooms


def _validate_schedule_list(
    value: object,
    *,
    allowed_rooms: list[str],
) -> list[dict]:
    if not isinstance(value, list):
        raise ValueError("Consultation schedules must be a list.")

    allowed_room_names = set(allowed_rooms)
    schedules: list[dict] = []

    for item in value:
        if not isinstance(item, dict):
            raise ValueError("Consultation schedules must contain objects.")
        if set(item) != CONSULTATION_SCHEDULE_FIELDS:
            raise ValueError("Invalid consultation schedule fields.")

        room = str(item.get("room") or "").strip()
        days = str(item.get("days") or "").strip()
        time = str(item.get("time") or "").strip()

        if not room or not days or not time:
            raise ValueError("Consultation schedules require room, days, and time.")
        if room not in allowed_room_names:
            raise ValueError("Consultation schedules must reference consultation rooms.")

        schedules.append(
            {
                "room": room,
                "days": days,
                "time": time,
            }
        )

    return schedules


def _validate_staff_profile_fields(
    payload: dict,
    *,
    existing_account: dict | None = None,
) -> dict:
    updates = {}

    if "assigned_programs" in payload:
        updates["assigned_programs"] = _validate_program_list(
            payload.get("assigned_programs")
        )

    if "office" in payload:
        updates["office"] = _validate_text_field(
            payload.get("office"),
            max_length=255,
        )

    if "support_statement" in payload:
        updates["support_statement"] = _validate_text_field(
            payload.get("support_statement")
        )

    existing_rooms = _decode_list(
        existing_account.get("consultation_rooms") if existing_account else None
    )

    if "consultation_rooms" in payload:
        updates["consultation_rooms"] = _validate_room_list(
            payload.get("consultation_rooms")
        )

    effective_rooms = updates.get("consultation_rooms", existing_rooms)

    if "consultation_schedules" in payload:
        updates["consultation_schedules"] = _validate_schedule_list(
            payload.get("consultation_schedules"),
            allowed_rooms=effective_rooms,
        )
    elif "consultation_rooms" in payload and existing_account:
        _validate_schedule_list(
            _decode_list(existing_account.get("consultation_schedules")),
            allowed_rooms=effective_rooms,
        )

    return updates


def _validate_common_account_updates(
    payload: dict,
    existing_account: dict,
) -> dict:
    updates = {}

    if "full_name" in payload:
        updates["full_name"] = _validate_full_name(payload.get("full_name"))

    if "email" in payload:
        updates["email"] = _validate_email(
            payload.get("email"),
            existing_account_id=existing_account["id"],
        )

    if "gender" in payload:
        updates["gender"] = _validate_gender(payload.get("gender"))

    return updates


def _is_duplicate_email_persistence_error(exc: Exception) -> bool:
    message = str(exc).lower()

    if (
        isinstance(exc, ValueError)
        and "email" in message
        and "already exists" in message
    ):
        return True

    errno = getattr(exc, "errno", None)
    if errno == 1062 and "email" in message:
        return True

    return False


def _create_account_with_duplicate_email_translation(**account_fields) -> dict:
    try:
        return create_account(**account_fields)
    except Exception as exc:
        if _is_duplicate_email_persistence_error(exc):
            raise FileExistsError("Email already exists.") from exc
        raise


def _update_account_fields_with_duplicate_email_translation(
    account_id: int,
    updates: dict,
    *,
    role: str,
) -> dict | None:
    try:
        return update_account_fields(account_id, updates, role=role)
    except Exception as exc:
        if _is_duplicate_email_persistence_error(exc):
            raise FileExistsError("Email already exists.") from exc
        raise


def create_account_service(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("Invalid request payload.")

    full_name = str(payload.get("full_name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    role = str(payload["role"] if "role" in payload else "student").strip().lower()

    gender = str(payload.get("gender", "")).strip() or None
    program = str(payload.get("program", "")).strip() or None

    if not full_name or not email or not password:
        raise ValueError("Missing required fields.")

    if not password.strip():
        raise ValueError("Password cannot be blank.")

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    full_name = _validate_full_name(full_name)
    email = _validate_email(email)
    role = _validate_role(role)

    if role == "student":
        program = _validate_student_program(program)

    gender = _validate_gender(gender)

    if role == "admin":
        unsupported_fields = set(payload) - ADMIN_ACCOUNT_CREATE_FIELDS
        if unsupported_fields:
            raise ValueError("Unsupported administrator account field.")

    staff_profile = {}
    if role == "staff":
        staff_profile = _validate_staff_profile_fields(payload)

    return _create_account_with_duplicate_email_translation(
        full_name=full_name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        student_number=None,
        staff_number=None,
        gender=gender,
        program=program,
        **staff_profile,
    )


def list_accounts_service(filters: dict) -> list[dict]:
    role = str(filters.get("role", "")).strip().lower() or None
    status = str(filters.get("status", "")).strip().lower() or None
    query = str(filters.get("q", "")).strip() or None

    if role:
        role = _validate_role(role)

    if status:
        status = _validate_status(status)

    return list_accounts(role=role, status=status, query=query)


def update_student_account_service(account_id: int, payload: dict) -> dict:
    if account_id <= 0:
        raise ValueError("Invalid account id.")

    if not isinstance(payload, dict):
        raise ValueError("Invalid request payload.")

    unsupported_fields = set(payload) - STUDENT_ACCOUNT_UPDATE_FIELDS
    if unsupported_fields:
        raise ValueError("Unsupported account update field.")

    existing_account = fetch_account_by_id(account_id, role="student")
    if not existing_account:
        raise LookupError("Student account not found.")

    updates = _validate_common_account_updates(payload, existing_account)

    if "program" in payload:
        updates["program"] = _validate_student_program(payload.get("program"))

    if not updates:
        raise ValueError("No supported account fields were provided.")

    updated_account = _update_account_fields_with_duplicate_email_translation(
        account_id,
        updates,
        role="student",
    )
    if not updated_account:
        raise LookupError("Student account not found.")

    return updated_account


def update_staff_account_service(account_id: int, payload: dict) -> dict:
    if account_id <= 0:
        raise ValueError("Invalid account id.")

    if not isinstance(payload, dict):
        raise ValueError("Invalid request payload.")

    unsupported_fields = set(payload) - STAFF_ACCOUNT_UPDATE_FIELDS
    if unsupported_fields:
        raise ValueError("Unsupported account update field.")

    existing_account = fetch_account_by_id(account_id, role="staff")
    if not existing_account:
        raise LookupError("Staff account not found.")

    updates = _validate_common_account_updates(payload, existing_account)
    updates.update(
        _validate_staff_profile_fields(
            payload,
            existing_account=existing_account,
        )
    )

    if not updates:
        raise ValueError("No supported account fields were provided.")

    updated_account = _update_account_fields_with_duplicate_email_translation(
        account_id,
        updates,
        role="staff",
    )
    if not updated_account:
        raise LookupError("Staff account not found.")

    return updated_account


def update_admin_account_service(account_id: int, payload: dict) -> dict:
    if account_id <= 0:
        raise ValueError("Invalid account id.")

    if not isinstance(payload, dict):
        raise ValueError("Invalid request payload.")

    unsupported_fields = set(payload) - ADMIN_ACCOUNT_UPDATE_FIELDS
    if unsupported_fields:
        raise ValueError("Unsupported account update field.")

    existing_account = fetch_account_by_id(account_id, role="admin")
    if not existing_account:
        raise LookupError("Administrator account not found.")

    updates = _validate_common_account_updates(payload, existing_account)

    if not updates:
        raise ValueError("No supported account fields were provided.")

    updated_account = _update_account_fields_with_duplicate_email_translation(
        account_id,
        updates,
        role="admin",
    )
    if not updated_account:
        raise LookupError("Administrator account not found.")

    return updated_account


def deactivate_admin_account_service(
    account_id: int,
    *,
    authenticated_admin_id: int,
) -> dict:
    if account_id <= 0:
        raise ValueError("Invalid account id.")

    if authenticated_admin_id <= 0:
        raise ValueError("Invalid authenticated administrator id.")

    if account_id == authenticated_admin_id:
        raise ValueError("Administrators cannot deactivate their own account.")

    existing_account = fetch_account_by_id(account_id, role="admin")
    if not existing_account:
        raise LookupError("Administrator account not found.")

    if existing_account.get("status") == "disabled":
        return existing_account

    updated_account = update_account_fields(
        account_id,
        {"status": "disabled"},
        role="admin",
    )
    if not updated_account:
        raise LookupError("Administrator account not found.")

    return updated_account


def deactivate_staff_account_service(account_id: int) -> dict:
    if account_id <= 0:
        raise ValueError("Invalid account id.")

    existing_account = fetch_account_by_id(account_id, role="staff")
    if not existing_account:
        raise LookupError("Staff account not found.")

    if existing_account.get("status") == "disabled":
        return existing_account

    updated_account = update_account_fields(
        account_id,
        {"status": "disabled"},
        role="staff",
    )
    if not updated_account:
        raise LookupError("Staff account not found.")

    return updated_account


def deactivate_student_account_service(account_id: int) -> dict:
    if account_id <= 0:
        raise ValueError("Invalid account id.")

    existing_account = fetch_account_by_id(account_id, role="student")
    if not existing_account:
        raise LookupError("Student account not found.")

    if existing_account.get("status") == "disabled":
        return existing_account

    updated_account = update_account_fields(
        account_id,
        {"status": "disabled"},
        role="student",
    )
    if not updated_account:
        raise LookupError("Student account not found.")

    return updated_account


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

    return user
