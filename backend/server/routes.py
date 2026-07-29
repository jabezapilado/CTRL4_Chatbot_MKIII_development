"""
Application Routes

Defines all frontend pages and REST API endpoints
for the CTRL4 Chatbot MK2.

Responsibilities

- Authentication
- Chat Processing
- Inquiry Management
- Appointment Management
- Dashboard APIs
- AI Integration
- Health Monitoring

CTRL4 Chatbot MK2

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from __future__ import annotations

import logging

# from flask import Blueprint, jsonify, request
from flask import Blueprint, jsonify, request, render_template, redirect, session

from datetime import datetime, timedelta

from .db import (
    current_time,
    fetch_rows,
    list_accounts,
    search_student_accounts,
    list_staff_appointments,
    load_settings,
    save_appointment,
    has_appointment_conflict,
    save_conversation_summary,
    list_conversation_summaries,
    save_escalation,
    save_inquiry,
    save_settings,
    get_appointment_by_id,
    update_appointment_status,
    create_account,
    fetch_account_by_email,
    fetch_account_by_student_number,
    fetch_account_by_staff_number,
    get_staff_by_program,
    get_student_by_id,
    update_counselor_notes,
    list_student_appointments,
    get_dashboard_stats,
)
from werkzeug.security import generate_password_hash

from .services import (
    ai_service,
    get_service_status,
    summary_service,
)

logger = logging.getLogger(__name__)

CATEGORY_AI_CHAT = "ai_chat"

api_bp = Blueprint("api", __name__)


def _get_logged_in_user():
    user = session.get("hau_user")
    return user if isinstance(user, dict) and user.get("email") else None


def _role_landing_path(user: dict) -> str:
    role = str(user.get("role", "student")).lower()
    if role in {"staff", "admin"}:
        return "/dashboard"
    return "/chatbot"


# Helper: students may only modify appointments at least 1 hour before scheduled time
def _student_can_modify_appointment(appointment: dict):
    appointment_datetime = datetime.strptime(
        f"{appointment['preferred_date']} {appointment['preferred_time_slot']}",
        "%Y-%m-%d %I:%M %p",
    )

    if appointment_datetime - datetime.now() < timedelta(hours=1):
        return False

    return True


@api_bp.before_request
def require_login_for_private_routes():
    public_paths = {"/", "/login", "/health", "/auth/login", "/auth/logout"}
    path = request.path

    if path.startswith("/static/") or path in public_paths:
        if path in {"/", "/login"} and _get_logged_in_user():
            return redirect(_role_landing_path(_get_logged_in_user()))
        return None

    user = _get_logged_in_user()
    if not user:
        if path.startswith("/api/") or path == "/chat":
            return jsonify({"error": "Login required."}), 401
        return redirect("/login?reason=session-required")

    role = str(user.get("role", "student")).lower()
    if path in {"/chatbot", "/appointment"} and role in {"staff", "admin"}:
        return redirect("/dashboard")
    if path in {"/dashboard", "/chatbot_admin"} and role == "student":
        return redirect("/chatbot")

    return None

#==========================================
#Frontend routes
@api_bp.get("/")
def home():
    return render_template("login.html")


@api_bp.get("/login")
def login():
    return render_template("login.html")


@api_bp.get("/chatbot")
def chatbot():
    return render_template("chatbot.html")


@api_bp.get("/appointment")
def appointment():
    return render_template("appointment.html")


@api_bp.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@api_bp.get("/chatbot_admin")
def chatbot_admin():
    return render_template("chatbot_admin.html")

#==========================================

@api_bp.get("/health")
def health():

    return jsonify(
        get_service_status()
    ), 200


@api_bp.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required."}), 400

    result = ai_service.respond(

        message=message,

        conversation=payload.get(
            "conversation",
            [],
        ),

    )
    
    logger.info(
        "AI response generated (emotion=%s, language=%s, escalated=%s, confidence=%.4f)",
        result.emotion,
        result.language,
        result.escalated,
        result.confidence,
    )
    
    if not result.success:

        logger.warning(
            "AIService failed for message: %s",
            message,
        )

        return jsonify({

            "success": False,

            "response": result.response,

        }), 200

    inquiry_id = save_inquiry(
        {
            "account_id": _get_logged_in_user()["id"],
            "inquiry_type": CATEGORY_AI_CHAT,
            "emotion_result": result.emotion,
            "escalated": result.escalated,
            "appointment_recommended": False,
            "created_at": current_time(),
        }
    )


    return jsonify({

        "success": result.success,

        "response": result.response,

        "emotion": result.emotion,

        "sentiment": result.sentiment,

        "language": result.language,

        "escalated": result.escalated,

        "confidence": round(
            result.confidence,
            4,
        ),

    }), 200

@api_bp.post("/chat/finalize")
def finalize_chat():
    payload = request.get_json(silent=True) or {}

    conversation = payload.get("conversation", [])

    if not conversation:
        return jsonify({"error": "Conversation is required."}), 400

    user = _get_logged_in_user()

    if not user:
        return jsonify({"error": "Login required."}), 401

    try:
        summary = summary_service.generate_summary(
            student_name=user["full_name"],
            conversation=conversation,
            topic=str(payload.get("topic", "general")),
            language=str(payload.get("language", "unknown")),
            emotion=str(payload.get("emotion", "neutral")),
            flagged=bool(payload.get("flagged", False)),
        )

        summary_id = save_conversation_summary(
            {
                "account_id": user["id"],
                "primary_concern": summary.primary_concern,
                "conversation_type": summary.conversation_type,
                "emotion_results": summary.emotion,
                "flagged_status": summary.flagged,
                "appointment_recommendation": summary.appointment_recommendation,
                "recommendations": summary.recommendations,
                "suggested_intervention": summary.suggested_intervention,
                "language_used": summary.language,
                "total_messages": summary.total_messages,
                "summary": summary.summary,
                "created_at": current_time(),
            }
        )

        if summary.flagged:
            save_escalation(
                {
                    "account_id": user["id"],
                    "summary_id": summary_id,
                    "status": "pending",
                    "created_at": current_time(),
                }
            )

        return jsonify(
            {
                "success": True,
                "summary_id": summary_id,
            }
        ), 200

    except Exception:
        logger.exception(
            "Failed to finalize conversation for user %s.",
            user["id"],
        )

        return jsonify(
            {
                "success": False,
                "error": "Unable to finalize conversation.",
            }
        ), 500 

@api_bp.get("/api/inquiries")
def inquiries():
    return jsonify({"items": fetch_rows("SELECT * FROM inquiries ORDER BY id DESC LIMIT 100")}), 200

@api_bp.get("/api/conversation-summaries")
def conversation_summaries():
    return jsonify({
        "items": list_conversation_summaries(),
    }), 200

@api_bp.get("/api/escalations")
def escalations():
    return jsonify({"items": fetch_rows("SELECT * FROM escalations ORDER BY id DESC LIMIT 100")}), 200


@api_bp.get("/api/appointments")
def appointments():
    user = _get_logged_in_user()

    if not user:
        return jsonify({"error": "Login required."}), 401

    role = str(user.get("role", "")).lower()

    if role != "staff":
        return jsonify(
            {
                "error": "Staff access required."
            }
        ), 403

    items = list_staff_appointments(user["id"])

    return jsonify({"items": items}), 200
    
@api_bp.get("/api/dashboard/stats")
def dashboard_stats():
    user = _get_logged_in_user()

    if not user:
        return jsonify({"error": "Login required."}), 401

    if str(user.get("role", "")).lower() != "staff":
        return jsonify({"error": "Staff access required."}), 403

    return jsonify(get_dashboard_stats()), 200

@api_bp.get("/api/my-appointments")
def my_appointments():
    user = _get_logged_in_user()

    if not user:
        return jsonify({"error": "Login required."}), 401
    if str(user.get("role", "student")).lower() != "student":
        return jsonify({"error": "Student access required."}), 403

    return jsonify(
        {
            "items": list_student_appointments(
                user["id"]
            )
        }
    ), 200



# Student cancellation endpoint
@api_bp.patch("/api/my-appointments/<int:appointment_id>/cancel")
def cancel_my_appointment(appointment_id: int):
    user = _get_logged_in_user()

    if not user:
        return jsonify({"error": "Login required."}), 401
    if str(user.get("role", "student")).lower() != "student":
        return jsonify({"error": "Student access required."}), 403

    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        return jsonify({"error": "Appointment not found."}), 404

    if appointment["account_id"] != user["id"]:
        return jsonify({"error": "You may only cancel your own appointments."}), 403

    if not _student_can_modify_appointment(appointment):
        return jsonify(
            {
                "error": "This appointment can no longer be modified because it is scheduled within the next hour."
            }
        ), 400

    if appointment["status"] != "pending":
        return jsonify(
            {"error": "Only pending appointments may be cancelled."}
        ), 400

    update_appointment_status(appointment_id, "cancelled")

    return jsonify({"status": "cancelled"}), 200


# Student rescheduling endpoint
@api_bp.post("/api/my-appointments/<int:appointment_id>/reschedule")
def reschedule_my_appointment(appointment_id: int):
    user = _get_logged_in_user()

    if not user:
        return jsonify({"error": "Login required."}), 401
    if str(user.get("role", "student")).lower() != "student":
        return jsonify({"error": "Student access required."}), 403

    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        return jsonify({"error": "Appointment not found."}), 404

    if appointment["account_id"] != user["id"]:
        return jsonify({"error": "You may only reschedule your own appointments."}), 403

    if appointment["status"] != "pending":
        return jsonify({"error": "Only pending appointments may be rescheduled."}), 400

    if not _student_can_modify_appointment(appointment):
        return jsonify({
            "error": "This appointment can no longer be modified because it is scheduled within the next hour."
        }), 400

    payload = request.get_json(silent=True) or {}

    required_fields = [
        "preferred_date",
        "preferred_time_slot",
    ]

    missing = [field for field in required_fields if not str(payload.get(field, "")).strip()]
    if missing:
        return jsonify({"error": "Missing required fields.", "fields": missing}), 400

    if has_appointment_conflict(
        payload["preferred_date"],
        payload["preferred_time_slot"],
    ):
        return jsonify({"error": "This schedule is already taken."}), 409

    new_id = save_appointment(
        {
            "account_id": appointment["account_id"],
            "contact_number": appointment["contact_number"],
            "appointment_category": appointment["appointment_category"],
            "appointment_mode": appointment["appointment_mode"],
            "preferred_date": payload["preferred_date"],
            "preferred_time_slot": payload["preferred_time_slot"],
            "reason": appointment["reason"],
            "status": "pending",
            "counselor_notes": None,
            "appointment_source": appointment["appointment_source"],
            "created_at": current_time(),
            "updated_at": current_time(),
        }
    )
    update_appointment_status(appointment_id, "cancelled")

    return jsonify({"status": "rescheduled", "appointment_id": new_id}), 201



@api_bp.get("/api/accounts")
def accounts():
    return jsonify({"items": list_accounts()}), 200


# Staff-only: Search student accounts
@api_bp.get("/api/accounts/search")
def search_accounts():
    user = _get_logged_in_user()

    if not user or str(user.get("role", "")).lower() != "staff":
        return jsonify({"error": "Staff access required."}), 403

    query = str(request.args.get("q", "")).strip()

    if not query:
        return jsonify({"items": []}), 200

    return jsonify(
        {
            "items": search_student_accounts(query)
        }
    ), 200


# Route: Create account (admin only)
@api_bp.post("/api/accounts")
def create_account_route():
    user = _get_logged_in_user()
    if not user or str(user.get("role", "")).lower() != "admin":
        return jsonify({"error": "Administrator access required."}), 403

    payload = request.get_json(silent=True) or {}

    full_name = str(payload.get("full_name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    role = str(payload.get("role", "student")).strip().lower()
    # student_number and staff_number are now generated in create_account()
    student_number = None
    staff_number = None
    gender = str(payload.get("gender", "")).strip() or None
    program = str(payload.get("program", "")).strip() or None

    if not full_name or not email or not password:
        return jsonify({"error": "Missing required fields."}), 400

    if fetch_account_by_email(email):
        return jsonify({"error": "Email already exists."}), 409

    if role == "student":
        # student_number is generated in create_account()
        if not program:
            return jsonify({"error": "Program is required."}), 400
        if not gender:
            return jsonify({"error": "Gender is required."}), 400
    elif role == "staff":
        # staff_number is generated in create_account()
        if not gender:
            return jsonify({"error": "Gender is required."}), 400
    elif role == "admin":
        if not gender:
            return jsonify({"error": "Gender is required."}), 400
    else:
        return jsonify({"error": "Invalid account role."}), 400

    account = create_account(
    full_name=full_name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        student_number=student_number,
        staff_number=staff_number,
        gender=gender,
        program=program,
    )

    return jsonify({
        "id": account["id"],
        "status": "created",
        "student_number": account["student_number"],
        "staff_number": account["staff_number"],
    }), 201


@api_bp.get("/api/settings")
def settings():
    return jsonify(load_settings()), 200


@api_bp.post("/api/settings")
def update_settings():
    payload = request.get_json(silent=True) or {}
    save_settings(payload)
    return jsonify({"status": "saved"}), 200



@api_bp.post("/api/appointments")
def create_appointment():
    payload = request.get_json(silent=True) or {}
    user = _get_logged_in_user()

    if not user:
        return jsonify({"error": "Login required."}), 401

    required_fields = [
        "contact_number",
        "appointment_category",
        "appointment_mode",
        "preferred_date",
        "preferred_time_slot",
        "reason",
    ]
    missing_fields = [field for field in required_fields if not str(payload.get(field, "")).strip()]

    if missing_fields:
        return jsonify({"error": "Missing required fields.", "fields": missing_fields}), 400
    
    if has_appointment_conflict(
        payload["preferred_date"],
        payload["preferred_time_slot"],
    ):
        return jsonify(
            {
                "error": "This schedule is already taken."
            }
        ), 409

    student = get_student_by_id(user["id"])

    if not student:
        return jsonify({"error": "Student account not found."}), 404

    student_program = str(student.get("program", "")).strip()

    counselor = get_staff_by_program(student_program)

    if counselor is None:
        return jsonify(
            {
                "error": "No counselor is currently assigned to your program. Please contact the Guidance Office."
            }
        ), 400

    appointment_id = save_appointment(
        {
            "account_id": user["id"],
            "contact_number": payload["contact_number"],
            "appointment_category": payload["appointment_category"],
            "appointment_mode": payload["appointment_mode"],
            "preferred_date": payload["preferred_date"],
            "preferred_time_slot": payload["preferred_time_slot"],
            "reason": payload["reason"],
            "status": "pending",
            "counselor_notes": None,
            "appointment_source": "chatbot",
            "created_at": current_time(),
            "updated_at": current_time(),
        }
    )

    return jsonify({"id": appointment_id, "status": "saved"}), 201


# Staff-only: create appointment for a student manually
@api_bp.post("/api/appointments/manual")
def create_manual_appointment():
    user = _get_logged_in_user()

    if not user or str(user.get("role", "")).lower() != "staff":
        return jsonify({"error": "Staff access required."}), 403

    payload = request.get_json(silent=True) or {}

    required_fields = [
        "account_id",
        "appointment_category",
        "appointment_mode",
        "preferred_date",
        "preferred_time_slot",
        "reason",
        "appointment_source",
    ]

    missing = [
        field
        for field in required_fields
        if not str(payload.get(field, "")).strip()
    ]

    if missing:
        return jsonify({"error": "Missing required fields.", "fields": missing}), 400

    if payload["appointment_source"] not in {
        "walk_in",
        "hotline",
        "messenger",
        "email",
        "staff_manual",
    }:
        return jsonify({"error": "Invalid appointment source."}), 400

    student = get_student_by_id(
        payload["account_id"]
    )

    if not student:
        return jsonify({"error": "Student account not found."}), 404

    counselor = get_staff_by_program(
        str(student["program"]).strip()
    )

    if counselor is None:
        return jsonify(
            {
                "error": (
                    "No counselor is currently assigned "
                    "to the student's program."
                )
            }
        ), 400

    if has_appointment_conflict(
        payload["preferred_date"],
        payload["preferred_time_slot"],
    ):
        return jsonify({"error": "This schedule is already taken."}), 409

    appointment_id = save_appointment(
        {
            "account_id": payload["account_id"],
            "contact_number": student.get("contact_number") or "",
            "appointment_category": payload["appointment_category"],
            "appointment_mode": payload["appointment_mode"],
            "preferred_date": payload["preferred_date"],
            "preferred_time_slot": payload["preferred_time_slot"],
            "reason": payload["reason"],
            "status": "approved",
            "counselor_notes": None,
            "appointment_source": payload["appointment_source"],
            "created_at": current_time(),
            "updated_at": current_time(),
        }
    )

    return jsonify({"id": appointment_id, "status": "created"}), 201

@api_bp.patch("/api/appointments/<int:appointment_id>")
def change_appointment(appointment_id: int):
    payload = request.get_json(silent=True) or {}
    user = _get_logged_in_user()

    if not user or str(user.get("role", "")).lower() != "staff":
        return jsonify({"error": "Staff access required."}), 403

    status = str(payload.get("status", "")).strip() or "pending"
    VALID_STATUSES = {
        "pending",
        "approved",
        "done",
        "did_not_attend",
        "cancelled",
    }

    if status not in VALID_STATUSES:
        return jsonify(
            {
                "error": "Invalid appointment status."
            }
        ), 400

    appointment = get_appointment_by_id(
        appointment_id
    )

    if not appointment:
        return jsonify(
            {
                "error": "Appointment not found."
            }
        ), 404

    allowed = {
        item["id"]
        for item in list_staff_appointments(user["id"])
    }

    if appointment_id not in allowed:
        return jsonify({"error": "Appointment not found."}), 404

    current_status = appointment["status"]

    ALLOWED_TRANSITIONS = {
        "pending": {
            "approved",
            "cancelled",
        },
        "approved": {
            "done",
            "did_not_attend",
            "cancelled",
        },
        "done": set(),
        "did_not_attend": set(),
        "cancelled": set(),
    }

    if status not in ALLOWED_TRANSITIONS.get(
        current_status,
        set(),
    ):
        return jsonify(
            {
                "error":
                f"Cannot change appointment status from "
                f"'{current_status}' to '{status}'."
            }
        ), 400

    update_appointment_status(appointment_id, status,)
    return jsonify({"status": "updated"}), 200

# =======================
# Staff-only appointment endpoints

@api_bp.get("/api/appointments/<int:appointment_id>")
def appointment_details(appointment_id: int):
    user = _get_logged_in_user()

    if not user or str(user.get("role", "")).lower() != "staff":
        return jsonify({"error": "Staff access required."}), 403

    rows = fetch_rows(
        """
        SELECT
            appointments.*,
            accounts.full_name AS student_name,
            accounts.email AS student_email,
            accounts.student_number,
            accounts.program
        FROM appointments
        JOIN accounts
            ON appointments.account_id = accounts.id
        WHERE appointments.id = %s
        LIMIT 1
        """,
        (appointment_id,),
    )

    if str(user.get("role", "")).lower() == "staff":
        allowed = {
            appointment["id"]
            for appointment in list_staff_appointments(user["id"])
        }

        if appointment_id not in allowed:
            return jsonify({"error": "Appointment not found."}), 404

    if not rows:
        return jsonify({"error": "Appointment not found."}), 404

    return jsonify(rows[0]), 200


@api_bp.patch("/api/appointments/<int:appointment_id>/notes")
def update_counselor_notes_route(appointment_id: int):
    user = _get_logged_in_user()

    if not user or str(user.get("role", "")).lower() != "staff":
        return jsonify({"error": "Staff access required."}), 403    

    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        return jsonify({"error": "Appointment not found."}), 404
    
    allowed = {
        item["id"]
        for item in list_staff_appointments(user["id"])
    }

    if appointment_id not in allowed:
        return jsonify(
            {
                "error": "Appointment not found."
            }
        ), 404

    payload = request.get_json(silent=True) or {}
    notes = str(payload.get("counselor_notes", "")).strip()
    
    status = str(appointment.get("status", "")).lower()

    if status == "pending":
        return jsonify(
            {
                "error": "Counselor notes cannot be added while the appointment is pending."
            }
        ), 400

    if status == "done" and not notes:
        return jsonify(
            {
                "error": "Counselor notes are required for completed appointments."
            }
        ), 400

    update_counselor_notes(
        appointment_id,
        notes,
    )

    return jsonify({"status": "saved"}), 200

