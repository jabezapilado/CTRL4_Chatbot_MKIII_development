from __future__ import annotations

import logging
from secrets import token_urlsafe

from flask import Blueprint, current_app, g, jsonify, request, session
from .csrf import get_csrf_token
from .services import student_session_service, transient_chat_service
from .services.account_service import (
    create_student_self_registration_service,
    login_service,
)
from .services.program_service import program_service
from .services.conversation_service import finalize_conversation


logger = logging.getLogger(__name__)

STUDENT_TERMS_ACCEPTED_SESSION_KEY = "student_terms_accepted"
STUDENT_SESSION_TOKEN_KEY = "student_session_token"

auth_bp = Blueprint("auth", __name__)


def _student_self_registration_available() -> bool:
    return bool(
        current_app.config.get("STUDENT_SELF_REGISTRATION_ENABLED")
        and str(current_app.config.get("STUDENT_SELF_REGISTRATION_CODE") or "")
    )


def _invalidate_replaced_student_session(user: dict) -> None:
    """Clear a student browser that no longer owns the active lease."""

    transient_chat_service.clear(getattr(session, "sid", ""), user.get("id"))
    session.clear()
    g.student_session_replaced = True
    logger.info("Rejected a replaced student browser session.")


def get_logged_in_user() -> dict | None:
    user = session.get("hau_user")
    if not isinstance(user, dict) or not user.get("email"):
        return None

    if str(user.get("role", "")).lower() != "student":
        return user

    token = session.get(STUDENT_SESSION_TOKEN_KEY)
    # Existing sessions from before this student-only safeguard remain valid
    # until their normal expiry. Every new student login receives a lease.
    if not isinstance(token, str) or not token:
        return user
    if student_session_service.is_current(user.get("id"), token):
        return user

    _invalidate_replaced_student_session(user)
    return None


def role_landing_path(user: dict) -> str:
    role = str(user.get("role", "student")).lower()

    if role == "staff":
        return "/dashboard"

    if role == "admin":
        return "/admin"

    return "/chatbot"


def _rotate_authenticated_session() -> None:
    """Replace the server-side session identifier after successful login."""
    regenerate = getattr(current_app.session_interface, "regenerate", None)
    if callable(regenerate):
        regenerate(session)


def _student_session_replacement_requested(payload: dict) -> bool:
    return payload.get("replace_existing_session") is True


def _finalize_replaced_student_session(user: dict) -> None:
    """Finish Device A with the established server-owned logout workflow."""

    student_session_service.finalize_replaced_session(
        user.get("id"),
        session.get(STUDENT_SESSION_TOKEN_KEY),
        user,
        transient_chat=transient_chat_service,
        finalizer=finalize_conversation,
    )


@auth_bp.post("/auth/login")
def login():
    payload = request.get_json(silent=True) or {}

    try:
        user = login_service(payload)
        is_student = str(user.get("role", "")).lower() == "student"
        has_other_student_session = is_student and student_session_service.has_other_active_session(
            user.get("id"), session.get(STUDENT_SESSION_TOKEN_KEY)
        )
        if has_other_student_session and not _student_session_replacement_requested(payload):
            return jsonify(
                {
                    "success": False,
                    "message": (
                        "This student account is currently active on another device. "
                        "Choose whether to replace that session."
                    ),
                    "errors": None,
                }
            ), 409
        if has_other_student_session:
            try:
                _finalize_replaced_student_session(user)
            except Exception as exc:
                logger.error(
                    "Student session replacement could not finalize the prior conversation "
                    "(exception_type=%s).",
                    type(exc).__name__,
                )
                return jsonify(
                    {
                        "success": False,
                        "message": "Unable to safely sign out the other device. Please try again.",
                        "errors": None,
                    }
                ), 503

        # Prevent session fixation by issuing a fresh authenticated session.
        session.clear()
        session["hau_user"] = user
        if is_student:
            session[STUDENT_TERMS_ACCEPTED_SESSION_KEY] = False
        _rotate_authenticated_session()
        if is_student:
            student_token = token_urlsafe(32)
            session[STUDENT_SESSION_TOKEN_KEY] = student_token
            if not student_session_service.register(
                user.get("id"),
                student_token,
                getattr(session, "sid", ""),
            ):
                raise RuntimeError("Unable to establish the student session.")
        session.permanent = True
        get_csrf_token()
    except ValueError as exc:
        logger.warning("Login validation failed.")
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 400
    except PermissionError as exc:
        logger.warning("Login denied.")
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 401
    except RuntimeError as exc:
        logger.warning("Login blocked.")
        return jsonify(
            {
                "success": False,
                "message": str(exc),
                "errors": None,
            }
        ), 403

    logger.info("Authenticated session established (role=%s).", user.get("role", "student"))
    return jsonify(
        {
            "success": True,
            "message": "Logged in successfully.",
            "data": user,
        }
    ), 200


@auth_bp.get("/auth/student-registration/programs")
def student_self_registration_programs():
    if not _student_self_registration_available():
        return jsonify(
            {
                "success": False,
                "message": "Student registration is unavailable.",
                "errors": None,
            }
        ), 404
    return jsonify(
        {
            "success": True,
            "message": "Programs retrieved successfully.",
            "data": {"items": program_service.list_programs()},
        }
    ), 200


@auth_bp.post("/auth/student-registration")
def student_self_registration():
    if not _student_self_registration_available():
        return jsonify(
            {
                "success": False,
                "message": "Student registration is unavailable.",
                "errors": None,
            }
        ), 404

    try:
        account = create_student_self_registration_service(
            request.get_json(silent=True) or {},
            registration_code=current_app.config.get("STUDENT_SELF_REGISTRATION_CODE"),
        )
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc), "errors": None}), 400
    except PermissionError as exc:
        return jsonify({"success": False, "message": str(exc), "errors": None}), 403
    except FileExistsError as exc:
        return jsonify({"success": False, "message": str(exc), "errors": None}), 409
    except Exception:
        logger.exception("Student self-registration failed.")
        return jsonify(
            {"success": False, "message": "Internal server error.", "errors": None}
        ), 500

    logger.info("Student self-registration created account %s", account["id"])
    return jsonify(
        {
            "success": True,
            "message": "Account created. Sign in to continue.",
            "data": {"student_number": account["student_number"]},
        }
    ), 201


@auth_bp.post("/auth/terms/accept")
def accept_student_terms():
    user = get_logged_in_user()
    if not user:
        return jsonify(
            {
                "success": False,
                "message": "Login required.",
                "errors": None,
            }
        ), 401
    if str(user.get("role", "")).lower() != "student":
        return jsonify(
            {
                "success": False,
                "message": "Student access required.",
                "errors": None,
            }
        ), 403

    session[STUDENT_TERMS_ACCEPTED_SESSION_KEY] = True
    return jsonify(
        {
            "success": True,
            "message": "Terms accepted.",
            "data": None,
        }
    ), 200


@auth_bp.get("/auth/session-status")
def session_status():
    """Provide a lightweight, same-origin student lease check for open chats."""

    user = get_logged_in_user()
    if not user:
        return jsonify(
            {
                "success": False,
                "message": "Login required.",
                "data": None,
            }
        ), 401

    return jsonify(
        {
            "success": True,
            "message": "Session is active.",
            "data": {"role": str(user.get("role", "student")).lower()},
        }
    ), 200


@auth_bp.post("/auth/logout")
def logout():
    user = get_logged_in_user()
    if not user:
        return jsonify(
            {
                "success": False,
                "message": "Login required.",
                "errors": None,
            }
        ), 401
    # The visible exchange is deliberately server-owned and tied to the opaque
    # session identifier. Remove it before clearing the session so a new login
    # cannot recover a prior authenticated session's chat.
    transient_chat_service.clear(getattr(session, "sid", ""), user.get("id"))
    student_session_service.clear_if_current(
        user.get("id"), session.get(STUDENT_SESSION_TOKEN_KEY)
    )
    session.clear()
    if user:
        logger.info("Authenticated session cleared.")
    return jsonify(
        {
            "success": True,
            "message": "Logged out successfully.",
            "data": None,
        }
    ), 200
