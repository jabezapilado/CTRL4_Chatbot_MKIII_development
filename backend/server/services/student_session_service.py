"""Server-owned single-device leases for student accounts only."""

from __future__ import annotations

import hmac
import logging
import time
from pathlib import Path
from typing import Any, Callable

from cachelib.file import FileSystemCache

from ..config import Config


_CACHE_PREFIX = "active-student-session:"
_INDEX_KEY = "active-student-session-index"
logger = logging.getLogger(__name__)
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

_EMOTION_PRIORITY = {
    "neutral": 0,
    "positive": 0,
    "unknown": 0,
    "support request": 1,
    "fear": 2,
    "sadness": 2,
    "anger": 2,
    "negative": 2,
    "crisis": 3,
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
        self._save(
            account_id,
            {
                "token": token_text,
                "session_id": session_text,
                "conversation": dict(_DEFAULT_CONVERSATION_CONTEXT),
                "last_chat_activity_at": int(time.time()),
            },
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

        prior_context = current["conversation"]
        current["conversation"] = self._conversation_context(
            topic=topic,
            language=language,
            emotion=self._most_relevant_emotion(
                prior_context.get("emotion"),
                emotion,
            ),
            flagged=flagged,
            review_only=review_only,
            escalation_reason=escalation_reason,
            appointment=appointment,
            active_summary_id=active_summary_id,
        )
        self._save(account_id, current)
        return True

    def record_chat_activity(self, account_id: object, token: object) -> bool:
        """Record a completed student chat exchange for idle finalization.

        Page loads, scrolling, and dashboard traffic do not extend this timer.
        That prevents a closed or abandoned browser from keeping its active
        conversation visible indefinitely.
        """

        current = self._current_for_token(account_id, token)
        if current is None:
            return False
        current["last_chat_activity_at"] = int(time.time())
        self._save(account_id, current)
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
        self._save(account_id, current)
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
        self._save(account_id, current)
        return True

    def clear_conversation_context(self, account_id: object, token: object) -> bool:
        """Prevent an already finalized chat from being finalized a second time."""

        current = self._current_for_token(account_id, token)
        if current is None:
            return False
        current["conversation"] = dict(_DEFAULT_CONVERSATION_CONTEXT)
        self._save(account_id, current)
        return True

    def is_current(self, account_id: object, token: object) -> bool:
        current = self._get(account_id)
        candidate = self._normalized_token(token)
        if not current or not candidate:
            return False
        if not hmac.compare_digest(current["token"], candidate):
            return False
        self._save(account_id, current)
        return True

    def clear_if_current(self, account_id: object, token: object) -> bool:
        current = self._current_for_token(account_id, token)
        if current is None:
            return False
        key = self._key(account_id)
        if key is None:
            return False
        self._cache.delete(key)
        self._remove_from_index(account_id)
        return True

    def finalize_idle_sessions(
        self,
        *,
        idle_timeout_seconds: int,
        transient_chat: Any,
        finalizer: Callable[..., dict],
        user_loader: Callable[[int], dict | None],
        now_epoch: int | None = None,
    ) -> dict[str, int]:
        """Finalize student chats abandoned beyond the approved idle window.

        Only compact lease metadata and the existing bounded transient chat are
        read.  No transcript is made durable by this maintenance operation.
        A failed finalization keeps the lease intact for a safe retry.
        """

        timeout = max(60, int(idle_timeout_seconds))
        now = int(time.time()) if now_epoch is None else int(now_epoch)
        report = {"checked": 0, "finalized": 0, "cleared": 0, "failed": 0}

        for account_id in self._indexed_account_ids():
            current = self._get(account_id)
            if current is None:
                self._remove_from_index(account_id)
                continue

            report["checked"] += 1
            last_activity = current.get("last_chat_activity_at")
            if not isinstance(last_activity, int):
                # Leases created before this safeguard get one full idle
                # window from their first maintenance pass instead of being
                # unexpectedly signed out during deployment.
                current["last_chat_activity_at"] = now
                self._save(account_id, current)
                continue
            if now - last_activity < timeout:
                continue

            context = current["conversation"]
            try:
                user = user_loader(account_id)
                conversation = transient_chat.get_visible_history(
                    current["session_id"], account_id
                )
                if user is not None and (
                    conversation or context.get("active_summary_id")
                ):
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
                    if not isinstance(result, dict) or not result.get("success"):
                        raise RuntimeError("Idle conversation finalization was unsuccessful.")
                    report["finalized"] += 1
                transient_chat.clear(current["session_id"], account_id)
                key = self._key(account_id)
                if key is not None:
                    self._cache.delete(key)
                self._remove_from_index(account_id)
                report["cleared"] += 1
            except Exception:
                report["failed"] += 1
                logger.exception(
                    "Idle student conversation finalization failed (account_id=%s).",
                    account_id,
                )

        return report

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
            "last_chat_activity_at": self._activity_timestamp(
                value.get("last_chat_activity_at")
            ),
        }

    def _save(self, account_id: object, value: dict) -> bool:
        key = self._key(account_id)
        if key is None:
            return False
        self._cache.set(key, value, timeout=self._timeout_seconds)
        self._add_to_index(account_id)
        return True

    def _indexed_account_ids(self) -> list[int]:
        value = self._cache.get(_INDEX_KEY)
        if not isinstance(value, list):
            return []
        account_ids: list[int] = []
        for item in value:
            try:
                account_id = int(item)
            except (TypeError, ValueError):
                continue
            if account_id > 0 and account_id not in account_ids:
                account_ids.append(account_id)
        return account_ids

    def _add_to_index(self, account_id: object) -> None:
        try:
            value = int(account_id)
        except (TypeError, ValueError):
            return
        if value <= 0:
            return
        account_ids = self._indexed_account_ids()
        if value not in account_ids:
            account_ids.append(value)
        self._cache.set(_INDEX_KEY, account_ids, timeout=self._timeout_seconds)

    def _remove_from_index(self, account_id: object) -> None:
        try:
            value = int(account_id)
        except (TypeError, ValueError):
            return
        account_ids = [item for item in self._indexed_account_ids() if item != value]
        if account_ids:
            self._cache.set(_INDEX_KEY, account_ids, timeout=self._timeout_seconds)
        else:
            self._cache.delete(_INDEX_KEY)

    @staticmethod
    def _activity_timestamp(value: object) -> int | None:
        try:
            timestamp = int(value)
        except (TypeError, ValueError):
            return None
        return timestamp if timestamp > 0 else None

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

    @staticmethod
    def _most_relevant_emotion(prior: object, current: object) -> str:
        """Keep a meaningful earlier concern from being overwritten by small talk."""

        prior_text = str(prior or "neutral").strip() or "neutral"
        current_text = str(current or "neutral").strip() or "neutral"
        prior_priority = _EMOTION_PRIORITY.get(prior_text.casefold(), 1)
        current_priority = _EMOTION_PRIORITY.get(current_text.casefold(), 1)
        return current_text if current_priority >= prior_priority else prior_text


__all__ = ["StudentSessionService"]
