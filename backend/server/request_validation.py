from __future__ import annotations

from flask import jsonify

from typing import Any

from .auth import get_logged_in_user

# Role constants
ROLE_STUDENT = "student"
ROLE_STAFF = "staff"
ROLE_ADMIN = "admin"

VALID_ROLES = frozenset({ROLE_STUDENT, ROLE_STAFF, ROLE_ADMIN})

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


def _normalize_role(role: str) -> str:
    normalized = str(role).strip().lower()
    if normalized not in VALID_ROLES:
        raise ValueError(f"Unsupported role: {role}")
    return normalized


def require_login() -> dict | None:
    """Ensure the user is logged in and return user info or None."""
    return get_logged_in_user()


def require_role(
    role: str,
) -> tuple[
    dict[str, Any] | None,
    tuple[Any, int] | None,
]:
    """Require the logged-in user to have a specific role."""
    user = get_logged_in_user()

    if not user:
        return None, _authorization_error("Login required.", 401)

    user_role = str(user.get("role", "")).lower()
    expected_role = _normalize_role(role)

    if user_role != expected_role:
        return None, _authorization_error(f"{role.capitalize()} access required.", 403)

    return user, None


def require_any_role(
    *roles: str,
) -> tuple[
    dict[str, Any] | None,
    tuple[Any, int] | None,
]:
    """Require the logged-in user to have any of the specified roles."""
    user = get_logged_in_user()

    if not user:
        return None, _authorization_error("Login required.", 401)

    user_role = str(user.get("role", "")).lower()
    allowed_roles = {_normalize_role(role) for role in roles}

    if user_role not in allowed_roles:
        return None, _authorization_error(
            "Insufficient permissions.",
            403,
        )

    return user, None