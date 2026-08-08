"""Focused contracts for bounded, server-owned active chat continuity."""

from __future__ import annotations

import importlib
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVICES_DIR = ROOT / "backend/server/services"
PACKAGE = "transient_chat_test.server.services"


def _load_service() -> type:
    if PACKAGE not in sys.modules:
        root_package = types.ModuleType("transient_chat_test")
        root_package.__path__ = []
        server_package = types.ModuleType("transient_chat_test.server")
        server_package.__path__ = []
        services_package = types.ModuleType(PACKAGE)
        services_package.__path__ = [str(SERVICES_DIR)]
        config = types.ModuleType("transient_chat_test.server.config")
        config.Config = object
        db = types.ModuleType("transient_chat_test.server.db")
        db.get_staff_by_program = lambda _program: None
        db.get_student_by_id = lambda _account_id: None
        db.load_persisted_settings = lambda _keys: {}
        sys.modules[root_package.__name__] = root_package
        sys.modules[server_package.__name__] = server_package
        sys.modules[services_package.__name__] = services_package
        sys.modules[config.__name__] = config
        sys.modules[db.__name__] = db
    return importlib.import_module(f"{PACKAGE}.transient_chat_service").TransientChatService


TransientChatService = _load_service()


class _Cache:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}
        self.deleted: list[str] = []

    def get(self, key: str):  # type: ignore[no-untyped-def]
        return self.values.get(key)

    def set(self, key: str, value: object, timeout: int) -> None:
        self.values[key] = value

    def delete(self, key: str) -> None:
        self.deleted.append(key)
        self.values.pop(key, None)


class TransientChatServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cache = _Cache()
        self.service = TransientChatService(cache=self.cache, timeout_seconds=60)

    def test_restores_only_the_same_authenticated_session_and_account(self) -> None:
        self.service.record_exchange("session-a", 11, [], "First message", "First reply")

        self.assertEqual(
            self.service.get_visible_history("session-a", 11),
            [
                {"from": "user", "text": "First message"},
                {"from": "bot", "text": "First reply"},
            ],
        )
        self.assertEqual(self.service.get_visible_history("session-a", 12), [])
        self.assertEqual(self.service.get_visible_history("session-b", 11), [])

    def test_logout_or_expiry_cleanup_removes_the_server_owned_exchange(self) -> None:
        self.service.record_exchange("session-a", 11, [], "Protected message", "Protected reply")
        self.service.clear("session-a", 11)

        self.assertEqual(self.service.get_visible_history("session-a", 11), [])
        self.assertEqual(len(self.cache.deleted), 1)

    def test_browser_history_is_only_a_compatibility_seed_and_current_message_is_excluded(self) -> None:
        prior = self.service.prior_history(
            "session-a",
            11,
            [
                {"from": "bot", "text": "Welcome"},
                {"from": "user", "text": "Current message"},
                {"from": "broken", "text": "ignore"},
            ],
            "Current message",
        )

        self.assertEqual(prior, [{"role": "assistant", "content": "Welcome"}])
