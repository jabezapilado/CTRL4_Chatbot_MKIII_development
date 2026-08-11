"""Server-owned single-device leases for student accounts only."""

from __future__ import annotations

import hmac
from pathlib import Path
from typing import Any, Callable

from cachelib.file import FileSystemCache

from ..config import Config


_CACHE_PREFIX = "active-student-session:"
_DEFAULT_CONVERSATION_CONTEXT = {
    "topic": "general",
    "language": "unknown",
    "emotion": "neutral",
    "flagged": False,
    "review_only": False,
    "escalation_reason": None,
    "appointment": None,
    "active_summary_id": None,
}


class StudentSessionService:
    """Track the one current browser session permitted for each student."""

    def __init__(
        self,
        *,
        cache: Any | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        config = Config() if cache is None or timeout_seconds is None else None
        self._timeout_seconds = timeout_seconds or int(
            config.PERMANENT_SESSION_LIFETIME.total_seconds()
        )
        if cache is None:
            assert config is not None
            # Use the configured session directory itself: production grants
            # the application user write access to that private directory,
            # while its parent may intentionally be root-owned.
            cache_directory = Path(config.SESSION_CACHE_DIR) / "student_sessions"
            cache_directory.mkdir(parents=True, exist_ok=True)
            cache_directory.chmod(0o700)
            cache = FileSystemCache(
                cache_dir=str(cache_directory),
                threshold=config.SESSION_CACHE_THRESHOLD,
                mode=0o700,
            )
        self._cache = cache

    def has_other_active_session(self, account_id: object, token: object) -> bool:
        current = self._get(account_id)
        candidate = self._normalized_token(token)
        return bool(
            current
            and (
                not candidate
                or not hmac.compare_digest(current["token"], candidate)
            )
        )

    def register(self, account_id: object, token: object, session_id: object) -> bool:
        key = self._key(account_id)
        token_text = self._normalized_token(token)
        session_text = str(session_id or "").strip()
        if key is None or not token_text or not session_text:
            return False
        self._cache.set(
            key,
            {
                "token": token_text,
                "session_id": session_text,
                "conversation": dict(_DEFAULT_CONVERSATION_CONTEXT),
            },
            timeout=self._timeout_seconds,
        )
        return True

    def update_conversation_context(
        self,
        account_id: object,
        token: object,
        *,
        topic: object,
        language: object,
        emotion: object,
        flagged: object,
        review_only: object,
        escalation_reason: object,
        appointment: object,
        active_summary_id: object,
    ) -> bool:
        """Keep only finalization metadata for the active student browser.

        The actual exchange remains in :class:`TransientChatService`.  This
        compact context exists solely so an approved device replacement can
        finish Device A through the normal conversation-finalization service.
        """

        current = self._current_for_token(account_id, token)
        if current is None:
            return False

        current["conversation"] = self._conversation_context(
            topic=topic,
            language=language,
            emotion=emotion,
            flagged=flagged,
            review_only=review_only,
            escalation_reason=escalation_reason,
            appointment=appointment,
            active_summary_id=active_summary_id,
        )
        self._cache.set(
            self._key(account_id),
            current,
            timeout=self._timeout_seconds,
        )
        return True

    def finalize_replaced_session(
        self,
        account_id: object,
        token: object,
        user: dict,
        *,
        transient_chat: Any,
        finalizer: Callable[..., dict],
    ) -> dict | None:
        """Finalize the old browser's active conversation before replacement.

        This keeps the existing staff visibility, summary, and escalation
        behavior intact.  The service never stores a durable transcript: it
        reads the bounded exchange from the existing transient-chat service,
        calls the established finalizer, and immediately clears that exchange.
        """

        current = self._get(account_id)
        candidate = self._normalized_token(token)
        if current is None or (
            candidate and hmac.compare_digest(current["token"], candidate)
        ):
            return None

        conversation = transient_chat.get_visible_history(
            current["session_id"],
            account_id,
        )
        context = current["conversation"]
        result = finalizer(
            user=user,
            conversation=conversation,
            topic=context["topic"],
            language=context["language"],
            emotion=context["emotion"],
            flagged=context["flagged"],
            review_only=context["review_only"],
            escalation_reason=context["escalation_reason"],
            appointment=context["appointment"],
            active_summary_id=context["active_summary_id"],
        )
        transient_chat.clear(current["session_id"], account_id)
        current["conversation"] = dict(_DEFAULT_CONVERSATION_CONTEXT)
        self._cache.set(
            self._key(account_id),
            current,
            timeout=self._timeout_seconds,
        )
        return result

    def set_appointment_context(
        self,
        account_id: object,
        token: object,
        appointment: object,
    ) -> bool:
        """Attach the existing appointment finalization metadata to a lease."""

        current = self._current_for_token(account_id, token)
        if current is None:
            return False
        context = current["conversation"]
        current["conversation"] = self._conversation_context(
            topic=context["topic"],
            language=context["language"],
            emotion=context["emotion"],
            flagged=context["flagged"],
            review_only=context["review_only"],
            escalation_reason=context["escalation_reason"],
            appointment=appointment,
            active_summary_id=context["active_summary_id"],
        )
        self._cache.set(
            self._key(account_id),
            current,
            timeout=self._timeout_seconds,
        )
        return True

    def clear_conversation_context(self, account_id: object, token: object) -> bool:
        """Prevent an already finalized chat from being finalized a second time."""

        current = self._current_for_token(account_id, token)
        if current is None:
            return False
        current["conversation"] = dict(_DEFAULT_CONVERSATION_CONTEXT)
        self._cache.set(
            self._key(account_id),
            current,
            timeout=self._timeout_seconds,
        )
        return True

    def is_current(self, account_id: object, token: object) -> bool:
        current = self._get(account_id)
        candidate = self._normalized_token(token)
        if not current or not candidate:
            return False
        if not hmac.compare_digest(current["token"], candidate):
            return False
        self._cache.set(
            self._key(account_id),
            current,
            timeout=self._timeout_seconds,
        )
        return True

    def clear_if_current(self, account_id: object, token: object) -> bool:
        current = self._current_for_token(account_id, token)
        if current is None:
            return False
        key = self._key(account_id)
        if key is None:
            return False
        self._cache.delete(key)
        return True

    def _current_for_token(self, account_id: object, token: object) -> dict | None:
        current = self._get(account_id)
        candidate = self._normalized_token(token)
        if not current or not candidate:
            return None
        if not hmac.compare_digest(current["token"], candidate):
            return None
        return current

    def _get(self, account_id: object) -> dict | None:
        key = self._key(account_id)
        if key is None:
            return None
        value = self._cache.get(key)
        if not isinstance(value, dict):
            return None
        token = self._normalized_token(value.get("token"))
        session_id = str(value.get("session_id") or "").strip()
        if not token or not session_id:
            return None
        return {
            "token": token,
            "session_id": session_id,
            "conversation": self._conversation_context_from_value(
                value.get("conversation")
            ),
        }

    @classmethod
    def _conversation_context_from_value(cls, value: object) -> dict:
        if not isinstance(value, dict):
            return dict(_DEFAULT_CONVERSATION_CONTEXT)
        return cls._conversation_context(
            topic=value.get("topic"),
            language=value.get("language"),
            emotion=value.get("emotion"),
            flagged=value.get("flagged"),
            review_only=value.get("review_only"),
            escalation_reason=value.get("escalation_reason"),
            appointment=value.get("appointment"),
            active_summary_id=value.get("active_summary_id"),
        )

    @staticmethod
    def _conversation_context(
        *,
        topic: object,
        language: object,
        emotion: object,
        flagged: object,
        review_only: object,
        escalation_reason: object,
        appointment: object,
        active_summary_id: object,
    ) -> dict:
        try:
            summary_id = int(active_summary_id)
        except (TypeError, ValueError):
            summary_id = None
        if summary_id is not None and summary_id <= 0:
            summary_id = None

        appointment_context = None
        if isinstance(appointment, dict):
            candidate = {
                key: str(appointment.get(key) or "").strip()
                for key in ("category", "preferred_date", "preferred_time_slot")
            }
            if all(candidate.values()):
                appointment_context = candidate

        return {
            "topic": str(topic or "general").strip() or "general",
            "language": str(language or "unknown").strip() or "unknown",
            "emotion": str(emotion or "neutral").strip() or "neutral",
            "flagged": bool(flagged),
            "review_only": bool(review_only),
            "escalation_reason": (
                str(escalation_reason).strip() if escalation_reason else None
            ),
            "appointment": appointment_context,
            "active_summary_id": summary_id,
        }

    @staticmethod
    def _key(account_id: object) -> str | None:
        try:
            value = int(account_id)
        except (TypeError, ValueError):
            return None
        return f"{_CACHE_PREFIX}{value}" if value > 0 else None

    @staticmethod
    def _normalized_token(token: object) -> str:
        return str(token or "").strip()


__all__ = ["StudentSessionService"]
