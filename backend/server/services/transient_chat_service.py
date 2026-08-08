"""Bounded, server-owned chat state for one authenticated browser session."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Final

from cachelib.file import FileSystemCache

from ..config import Config
from .conversation_history import (
    MAX_HISTORY_MESSAGE_CHARACTERS,
    MAX_HISTORY_MESSAGES,
    normalize_conversation_history,
)


_CACHE_PREFIX: Final[str] = "transient-chat:"


class TransientChatService:
    """Keep visible exchanges on the server without durable transcript storage."""

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
            cache_directory = Path(config.SESSION_CACHE_DIR).parent / "transient_chat"
            cache_directory.mkdir(parents=True, exist_ok=True)
            cache_directory.chmod(0o700)
            cache = FileSystemCache(
                cache_dir=str(cache_directory),
                threshold=config.SESSION_CACHE_THRESHOLD,
                mode=0o700,
            )
        self._cache = cache

    def get_visible_history(
        self,
        session_id: object,
        account_id: object,
    ) -> list[dict[str, str]]:
        key = self._cache_key(session_id, account_id)
        if key is None:
            return []
        return self._visible_entries(self._cache.get(key))

    def prior_history(
        self,
        session_id: object,
        account_id: object,
        browser_history: object,
        incoming_message: object,
    ) -> list[dict[str, str]]:
        """Use server state when present; safely seed it from a legacy payload once."""

        stored = self.get_visible_history(session_id, account_id)
        if stored:
            return self._canonical(stored)

        seeded = self._canonical(browser_history)
        message = str(incoming_message).strip()
        if seeded and seeded[-1]["role"] == "user" and seeded[-1]["content"] == message:
            seeded.pop()
        return seeded

    def record_exchange(
        self,
        session_id: object,
        account_id: object,
        prior_history: object,
        user_message: object,
        assistant_message: object,
    ) -> None:
        key = self._cache_key(session_id, account_id)
        if key is None:
            return
        canonical = self._canonical(prior_history)
        canonical.extend(
            self._canonical(
                [
                    {"role": "user", "content": str(user_message)},
                    {"role": "assistant", "content": str(assistant_message)},
                ]
            )
        )
        self._cache.set(key, self._visible_entries(canonical), timeout=self._timeout_seconds)

    def clear(self, session_id: object, account_id: object) -> None:
        key = self._cache_key(session_id, account_id)
        if key is not None:
            self._cache.delete(key)

    @staticmethod
    def _canonical(entries: object) -> list[dict[str, str]]:
        return normalize_conversation_history(entries)

    @staticmethod
    def _visible_entries(entries: object) -> list[dict[str, str]]:
        return [
            {
                "from": "user" if item["role"] == "user" else "bot",
                "text": item["content"],
            }
            for item in normalize_conversation_history(entries)
        ]

    @staticmethod
    def _cache_key(session_id: object, account_id: object) -> str | None:
        session_text = str(session_id or "").strip()
        try:
            account_value = int(account_id)
        except (TypeError, ValueError):
            return None
        if not session_text or account_value <= 0:
            return None
        digest = hashlib.sha256(
            f"{session_text}\0{account_value}".encode("utf-8")
        ).hexdigest()
        return _CACHE_PREFIX + digest


__all__ = ["TransientChatService"]
