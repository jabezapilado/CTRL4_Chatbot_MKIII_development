import logging
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    session,
    make_response,
)

from ..auth import get_logged_in_user, role_landing_path
from ..request_validation import (
    ROLE_ADMIN,
    ROLE_STAFF,
    ROLE_STUDENT,
)
from ..services import transient_chat_service

logger = logging.getLogger(__name__)

frontend_bp = Blueprint("frontend", __name__)


@frontend_bp.get("/")
def home():
    return render_template("login.html")


@frontend_bp.get("/login")
def login():
    return render_template("login.html")


@frontend_bp.get("/chatbot")
def chatbot():
    user = get_logged_in_user() or {}
    active_chat = []
    if str(user.get("role", "")).lower() == ROLE_STUDENT:
        active_chat = transient_chat_service.get_visible_history(
            getattr(session, "sid", ""),
            user.get("id"),
        )
    response = make_response(render_template("chatbot.html", active_chat=active_chat))
    response.headers["Cache-Control"] = "no-store"
    return response


@frontend_bp.get("/case-status")
def case_status():
    return render_template("case_status.html")


@frontend_bp.get("/appointment")
def appointment():
    return render_template("appointment.html")


@frontend_bp.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@frontend_bp.get("/admin")
def admin_accounts():
    return render_template(
        "admin.html",
    )


@frontend_bp.before_request
def require_login_for_private_routes():
    public_paths = {"/", "/login", "/health", "/auth/login", "/auth/logout"}
    path = request.path

    if path.startswith("/static/") or path in public_paths:
        user = get_logged_in_user()
        if path in {"/", "/login"} and user:
            return redirect(role_landing_path(user))
        return None

    user = get_logged_in_user()
    logger.debug("Frontend request: path=%s authenticated=%s", path, bool(user))
    if not user:
        if path.startswith("/api/") or path == "/chat":
            logger.warning("Unauthorized API access to %s", path)
            return jsonify(
                {
                    "success": False,
                    "message": "Login required.",
                    "errors": None,
                }
            ), 401
        logger.info("Redirecting unauthenticated user to login from %s", path)
        return redirect("/login?reason=session-required")

    role = str(user.get("role", ROLE_STUDENT)).lower()
    if path in {"/chatbot", "/appointment", "/case-status"} and role in {
        ROLE_STAFF,
        ROLE_ADMIN,
    }:
        return redirect("/dashboard")
    if path == "/dashboard" and role == ROLE_ADMIN:
        return redirect("/admin")
    if path == "/dashboard" and role == ROLE_STUDENT:
        return redirect("/chatbot")
    if path == "/admin" and role != ROLE_ADMIN:
        return redirect(role_landing_path(user))

    return None
