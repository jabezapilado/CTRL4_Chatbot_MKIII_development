from __future__ import annotations

from flask import jsonify

from typing import Any

from .auth import get_logged_in_user


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
        return None, (jsonify({"error": "Login required."}), 401)

    if str(user.get("role", "")).lower() != role.lower():
        return None, (
            jsonify({"error": f"{role.capitalize()} access required."}),
            403,
        )

    return user, None