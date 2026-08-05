import logging
from flask import Blueprint, jsonify, request

from ..request_validation import require_role
from ..services.case_note_service import (
    create_staff_case_note,
    list_staff_case_notes,
    update_staff_case_note,
)
from ..services.referral_service import (
    add_staff_referral_note,
    create_staff_referral,
    list_staff_referrals,
    update_staff_referral_status,
)
from ..services.intervention_service import (
    create_staff_intervention,
    list_staff_interventions,
    record_staff_intervention_outcome,
    update_staff_intervention_progress,
)
from ..services.confidentiality_service import (
    get_staff_case_confidentiality,
    update_staff_case_confidentiality,
)
from ..services.conversation_service import (
    get_staff_flagged_conversation,
    list_student_cases,
    list_staff_flagged_conversations,
    list_staff_conversation_summaries,
    list_staff_escalations,
    list_staff_inquiries,
    mark_staff_flagged_conversation_reviewed,
)

logger = logging.getLogger(__name__)

conversation_bp = Blueprint(
    "conversation",
    __name__,
    url_prefix="/api",
)


@conversation_bp.get("/inquiries")
def inquiries():
    _, error = require_role("staff")
    if error:
        return error
    try:
        items = list_staff_inquiries()
        return jsonify(
            {
                "success": True,
                "message": "Inquiries retrieved successfully.",
                "data": {
                    "items": items,
                },
            }
        ), 200
    except Exception:
        logger.exception("Failed to retrieve inquiries.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@conversation_bp.get("/conversation-summaries")
def conversation_summaries():
    _, error = require_role("staff")
    if error:
        return error
    try:
        items = list_staff_conversation_summaries()
        return jsonify(
            {
                "success": True,
                "message": "Conversation summaries retrieved successfully.",
                "data": {
                    "items": items,
                },
            }
        ), 200
    except Exception:
        logger.exception("Failed to retrieve conversation summaries.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@conversation_bp.get("/escalations")
def escalations():
    _, error = require_role("staff")
    if error:
        return error
    try:
        items = list_staff_escalations()
        return jsonify(
            {
                "success": True,
                "message": "Escalations retrieved successfully.",
                "data": {
                    "items": items,
                },
            }
        ), 200
    except Exception:
        logger.exception("Failed to retrieve escalations.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@conversation_bp.get("/flagged-conversations")
def flagged_conversations():
    _, error = require_role("staff")
    if error:
        return error
    try:
        items = list_staff_flagged_conversations()
        return jsonify(
            {
                "success": True,
                "message": "Flagged conversations retrieved successfully.",
                "data": {
                    "items": items,
                },
            }
        ), 200
    except Exception:
        logger.exception("Failed to retrieve flagged conversations.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@conversation_bp.get("/student/cases")
def student_cases():
    user, error = require_role("student")
    if error:
        return error
    try:
        items = list_student_cases(user)
        return jsonify(
            {
                "success": True,
                "message": "Case statuses retrieved successfully.",
                "data": {"items": items},
            }
        ), 200
    except Exception:
        logger.exception("Failed to retrieve student case statuses.")
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@conversation_bp.get("/flagged-conversations/<int:summary_id>")
def flagged_conversation(summary_id: int):
    _, error = require_role("staff")
    if error:
        return error
    try:
        item = get_staff_flagged_conversation(summary_id)
        if item is None:
            return jsonify(
                {
                    "success": False,
                    "message": "Flagged conversation not found.",
                    "errors": None,
                }
            ), 404
        return jsonify(
            {
                "success": True,
                "message": "Flagged conversation retrieved successfully.",
                "data": item,
            }
        ), 200
    except Exception:
        logger.exception("Failed to retrieve flagged conversation %s.", summary_id)
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@conversation_bp.patch("/flagged-conversations/<int:summary_id>/review")
def review_flagged_conversation(summary_id: int):
    _, error = require_role("staff")
    if error:
        return error
    try:
        item = mark_staff_flagged_conversation_reviewed(summary_id)
        if item is None:
            return jsonify(
                {
                    "success": False,
                    "message": "Flagged conversation not found.",
                    "errors": None,
                }
            ), 404
        return jsonify(
            {
                "success": True,
                "message": "Flagged conversation marked as reviewed.",
                "data": item,
            }
        ), 200
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 409
    except Exception:
        logger.exception("Failed to review flagged conversation %s.", summary_id)
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@conversation_bp.get("/flagged-conversations/<int:summary_id>/confidentiality")
def case_confidentiality(summary_id: int):
    _, error = require_role("staff")
    if error:
        return error
    try:
        confidentiality = get_staff_case_confidentiality(summary_id)
        return jsonify(
            {
                "success": True,
                "message": "Case confidentiality retrieved successfully.",
                "data": confidentiality,
            }
        ), 200
    except LookupError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 404
    except Exception:
        logger.exception("Failed to retrieve confidentiality for case %s.", summary_id)
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@conversation_bp.patch("/flagged-conversations/<int:summary_id>/confidentiality")
def update_case_confidentiality(summary_id: int):
    user, error = require_role("staff")
    if error:
        return error
    payload = request.get_json(silent=True) or {}

    try:
        confidentiality = update_staff_case_confidentiality(
            user,
            summary_id,
            str(payload.get("confidentiality_status", "")),
            payload.get("confidentiality_reason"),
        )
    except LookupError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 404
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 400
    except Exception:
        logger.exception("Failed to update confidentiality for case %s.", summary_id)
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    logger.info("Staff %s updated confidentiality for case %s.", user["id"], summary_id)
    return jsonify(
        {
            "success": True,
            "message": "Case confidentiality updated successfully.",
            "data": confidentiality,
        }
    ), 200


@conversation_bp.get("/flagged-conversations/<int:summary_id>/notes")
def case_notes(summary_id: int):
    _, error = require_role("staff")
    if error:
        return error
    try:
        items = list_staff_case_notes(summary_id)
        return jsonify(
            {
                "success": True,
                "message": "Counselor notes retrieved successfully.",
                "data": {"items": items},
            }
        ), 200
    except LookupError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 404
    except Exception:
        logger.exception("Failed to retrieve counselor notes for case %s.", summary_id)
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@conversation_bp.post("/flagged-conversations/<int:summary_id>/notes")
def create_case_note(summary_id: int):
    user, error = require_role("staff")
    if error:
        return error
    payload = request.get_json(silent=True) or {}

    try:
        note = create_staff_case_note(
            user,
            summary_id,
            str(payload.get("note_text", "")),
        )
    except LookupError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 404
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 400
    except Exception:
        logger.exception("Failed to create counselor note for case %s.", summary_id)
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    logger.info("Staff %s created counselor note for case %s.", user["id"], summary_id)
    return jsonify(
        {
            "success": True,
            "message": "Counselor note created successfully.",
            "data": note,
        }
    ), 201


@conversation_bp.patch(
    "/flagged-conversations/<int:summary_id>/notes/<int:note_id>"
)
def update_case_note(summary_id: int, note_id: int):
    user, error = require_role("staff")
    if error:
        return error
    payload = request.get_json(silent=True) or {}

    try:
        note = update_staff_case_note(
            user,
            summary_id,
            note_id,
            str(payload.get("note_text", "")),
        )
    except LookupError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 404
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 400
    except Exception:
        logger.exception(
            "Failed to update counselor note %s for case %s.",
            note_id,
            summary_id,
        )
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    logger.info(
        "Staff %s updated counselor note %s for case %s.",
        user["id"],
        note_id,
        summary_id,
    )
    return jsonify(
        {
            "success": True,
            "message": "Counselor note updated successfully.",
            "data": note,
        }
    ), 200


@conversation_bp.get("/flagged-conversations/<int:summary_id>/referrals")
def referrals(summary_id: int):
    _, error = require_role("staff")
    if error:
        return error
    try:
        items = list_staff_referrals(summary_id)
        return jsonify(
            {
                "success": True,
                "message": "Referrals retrieved successfully.",
                "data": {"items": items},
            }
        ), 200
    except LookupError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 404
    except Exception:
        logger.exception("Failed to retrieve referrals for case %s.", summary_id)
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@conversation_bp.post("/flagged-conversations/<int:summary_id>/referrals")
def create_referral(summary_id: int):
    user, error = require_role("staff")
    if error:
        return error
    payload = request.get_json(silent=True) or {}

    try:
        referral = create_staff_referral(
            user,
            summary_id,
            str(payload.get("destination", "")),
            str(payload.get("referral_reason", "")),
            payload.get("note_text"),
        )
    except LookupError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 404
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 400
    except Exception:
        logger.exception("Failed to create referral for case %s.", summary_id)
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    logger.info("Staff %s created referral for case %s.", user["id"], summary_id)
    return jsonify(
        {
            "success": True,
            "message": "Referral created successfully.",
            "data": referral,
        }
    ), 201


@conversation_bp.patch(
    "/flagged-conversations/<int:summary_id>/referrals/<int:referral_id>/status"
)
def update_referral_status(summary_id: int, referral_id: int):
    user, error = require_role("staff")
    if error:
        return error
    payload = request.get_json(silent=True) or {}

    try:
        referral = update_staff_referral_status(
            user,
            summary_id,
            referral_id,
            str(payload.get("status", "")),
        )
    except LookupError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 404
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 400
    except Exception:
        logger.exception(
            "Failed to update referral %s for case %s.",
            referral_id,
            summary_id,
        )
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    logger.info(
        "Staff %s updated referral %s for case %s.",
        user["id"],
        referral_id,
        summary_id,
    )
    return jsonify(
        {
            "success": True,
            "message": "Referral status updated successfully.",
            "data": referral,
        }
    ), 200


@conversation_bp.post(
    "/flagged-conversations/<int:summary_id>/referrals/<int:referral_id>/notes"
)
def add_referral_note(summary_id: int, referral_id: int):
    user, error = require_role("staff")
    if error:
        return error
    payload = request.get_json(silent=True) or {}

    try:
        referral = add_staff_referral_note(
            user,
            summary_id,
            referral_id,
            str(payload.get("note_text", "")),
        )
    except LookupError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 404
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 400
    except Exception:
        logger.exception(
            "Failed to add note to referral %s for case %s.",
            referral_id,
            summary_id,
        )
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    logger.info(
        "Staff %s added note to referral %s for case %s.",
        user["id"],
        referral_id,
        summary_id,
    )
    return jsonify(
        {
            "success": True,
            "message": "Referral note added successfully.",
            "data": referral,
        }
    ), 201


@conversation_bp.get("/flagged-conversations/<int:summary_id>/interventions")
def interventions(summary_id: int):
    _, error = require_role("staff")
    if error:
        return error
    try:
        items = list_staff_interventions(summary_id)
        return jsonify(
            {
                "success": True,
                "message": "Interventions retrieved successfully.",
                "data": {"items": items},
            }
        ), 200
    except LookupError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 404
    except Exception:
        logger.exception("Failed to retrieve interventions for case %s.", summary_id)
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500


@conversation_bp.post("/flagged-conversations/<int:summary_id>/interventions")
def create_intervention(summary_id: int):
    user, error = require_role("staff")
    if error:
        return error
    payload = request.get_json(silent=True) or {}

    try:
        intervention = create_staff_intervention(
            user,
            summary_id,
            str(payload.get("intervention_type", "")),
            str(payload.get("objective", "")),
        )
    except LookupError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 404
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 400
    except Exception:
        logger.exception("Failed to create intervention for case %s.", summary_id)
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    logger.info("Staff %s created intervention for case %s.", user["id"], summary_id)
    return jsonify(
        {
            "success": True,
            "message": "Intervention created successfully.",
            "data": intervention,
        }
    ), 201


@conversation_bp.patch(
    "/flagged-conversations/<int:summary_id>/interventions/<int:intervention_id>/progress"
)
def update_intervention_progress(summary_id: int, intervention_id: int):
    user, error = require_role("staff")
    if error:
        return error
    payload = request.get_json(silent=True) or {}

    try:
        intervention = update_staff_intervention_progress(
            user,
            summary_id,
            intervention_id,
            str(payload.get("progress_status", "")),
        )
    except LookupError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 404
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 400
    except Exception:
        logger.exception(
            "Failed to update intervention %s for case %s.",
            intervention_id,
            summary_id,
        )
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    logger.info(
        "Staff %s updated intervention %s for case %s.",
        user["id"],
        intervention_id,
        summary_id,
    )
    return jsonify(
        {
            "success": True,
            "message": "Intervention progress updated successfully.",
            "data": intervention,
        }
    ), 200


@conversation_bp.patch(
    "/flagged-conversations/<int:summary_id>/interventions/<int:intervention_id>/outcome"
)
def record_intervention_outcome(summary_id: int, intervention_id: int):
    user, error = require_role("staff")
    if error:
        return error
    payload = request.get_json(silent=True) or {}

    try:
        intervention = record_staff_intervention_outcome(
            user,
            summary_id,
            intervention_id,
            str(payload.get("outcome", "")),
        )
    except LookupError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 404
    except ValueError as error:
        return jsonify(
            {
                "success": False,
                "message": str(error),
                "errors": None,
            }
        ), 400
    except Exception:
        logger.exception(
            "Failed to record outcome for intervention %s in case %s.",
            intervention_id,
            summary_id,
        )
        return jsonify(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": None,
            }
        ), 500

    logger.info(
        "Staff %s recorded outcome for intervention %s in case %s.",
        user["id"],
        intervention_id,
        summary_id,
    )
    return jsonify(
        {
            "success": True,
            "message": "Intervention outcome recorded successfully.",
            "data": intervention,
        }
    ), 200
