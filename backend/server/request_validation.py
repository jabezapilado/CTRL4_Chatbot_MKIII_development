from __future__ import annotations

from flask import jsonify

from typing import Any

from .auth import get_logged_in_user

# Role constants
ROLE_STUDENT = "student"
ROLE_STAFF = "staff"
ROLE_ADMIN = "admin"
def _authorization_error(message: str, status: int) -> tuple[Any, int]:
    return (
        jsonify(
            {
                "success": False,
                "message": message,
                "errors": None,
            }
        ),
        status,
    )



def require_login() -> dict | None:
    return get_logged_in_user()


def require_role(
    role: str,
) -> tuple[
    dict[str, Any] | None,
    tuple[Any, int] | None,
]:
    user = get_logged_in_user()

    if not user:
        return None, _authorization_error("Login required.", 401)

    user_role = str(user.get("role", "")).lower()
    role_lower = role.lower()
    if role_lower == ROLE_STUDENT:
        expected_role = ROLE_STUDENT
    elif role_lower == ROLE_STAFF:
        expected_role = ROLE_STAFF
    elif role_lower == ROLE_ADMIN:
        expected_role = ROLE_ADMIN
    else:
        expected_role = role_lower

    if user_role != expected_role:
        return None, _authorization_error(f"{role.capitalize()} access required.", 403)

    return user, None


def require_any_role(
    *roles: str,
) -> tuple[
    dict[str, Any] | None,
    tuple[Any, int] | None,
]:
    user = get_logged_in_user()

    if not user:
        return None, _authorization_error("Login required.", 401)

    user_role = str(user.get("role", "")).lower()
    allowed_roles = {role.lower() for role in roles}

    if user_role not in allowed_roles:
        return None, _authorization_error(
            "Insufficient permissions.",
            403,
        )

    return user, None