import logging
from flask import Blueprint, render_template, request, jsonify, redirect

from ..auth import get_logged_in_user, role_landing_path

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
    return render_template("chatbot.html")


@frontend_bp.get("/appointment")
def appointment():
    return render_template("appointment.html")


@frontend_bp.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@frontend_bp.get("/chatbot_admin")
def chatbot_admin():
    return render_template("chatbot_admin.html")


@frontend_bp.before_request
def require_login_for_private_routes():
    public_paths = {"/", "/login", "/health", "/auth/login", "/auth/logout"}
    path = request.path

    if path.startswith("/static/") or path in public_paths:
        if path in {"/", "/login"} and get_logged_in_user():
            return redirect(role_landing_path(get_logged_in_user()))
        return None

    user = get_logged_in_user()
    logger.debug("Frontend request: path=%s authenticated=%s", path, bool(user))
    if not user:
        if path.startswith("/api/") or path == "/chat":
            logger.warning("Unauthorized API access to %s", path)
            return jsonify({"error": "Login required."}), 401
        logger.info("Redirecting unauthenticated user to login from %s", path)
        return redirect("/login?reason=session-required")

    role = str(user.get("role", "student")).lower()
    if path in {"/chatbot", "/appointment"} and role in {"staff", "admin"}:
        return redirect("/dashboard")
    if path in {"/dashboard", "/chatbot_admin"} and role == "student":
        return redirect("/chatbot")

    return None
