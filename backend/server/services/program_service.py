"""Settings-backed academic program catalog owned by administrator account management."""

from __future__ import annotations

import re
from typing import Any, Callable, Final

from ..config import Config
from ..db import load_persisted_settings, save_settings


PROGRAM_CATALOG_KEY: Final[str] = "programCatalog"
MAX_PROGRAM_CODE_LENGTH: Final[int] = 80
MAX_PROGRAM_NAME_LENGTH: Final[int] = 160


def _decode(value: object) -> object:
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    if isinstance(value, str):
        import json

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _normalized_code(value: object) -> str:
    code = str(value or "").strip().upper()
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9_-]{0,79}", code):
        raise ValueError("Program code is invalid.")
    return code


def _normalized_name(value: object) -> str:
    name = " ".join(str(value or "").split())
    if not name:
        raise ValueError("Program display name is required.")
    if len(name) > MAX_PROGRAM_NAME_LENGTH:
        raise ValueError("Program display name is too long.")
    return name


def _catalog_entry(value: object, index: int) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("Each program must be an object.")
    code = _normalized_code(value.get("code"))
    display_name = _normalized_name(value.get("display_name"))
    active = value.get("active", True)
    if not isinstance(active, bool):
        raise ValueError("Program active status must be true or false.")
    order = value.get("order", index + 1)
    if not isinstance(order, int) or isinstance(order, bool) or order < 0:
        raise ValueError("Program order is invalid.")
    return {
        "code": code,
        "display_name": display_name,
        "active": active,
        "order": order,
    }


def normalize_program_catalog(value: object) -> list[dict[str, Any]]:
    catalog = _decode(value)
    if not isinstance(catalog, list):
        raise ValueError("Program catalog must be a list.")
    entries = [_catalog_entry(entry, index) for index, entry in enumerate(catalog)]
    if len({entry["code"] for entry in entries}) != len(entries):
        raise ValueError("Program codes must be unique.")
    if len({entry["display_name"].casefold() for entry in entries}) != len(entries):
        raise ValueError("Program display names must be unique.")
    return sorted(entries, key=lambda entry: (entry["order"], entry["display_name"]))


def _bootstrap_catalog() -> list[dict[str, Any]]:
    programs = Config().PROGRAMS
    return [
        {
            "code": re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_"),
            "display_name": name,
            "active": True,
            "order": index + 1,
        }
        for index, name in enumerate(programs)
    ]


class ProgramService:
    def __init__(
        self,
        *,
        load: Callable[[tuple[str, ...]], dict[str, Any]] = load_persisted_settings,
        save: Callable[[dict[str, Any]], None] = save_settings,
    ) -> None:
        self._load = load
        self._save = save

    def seed_program_catalog(self) -> dict[str, list[str]]:
        persisted = self._load((PROGRAM_CATALOG_KEY,))
        if PROGRAM_CATALOG_KEY in persisted:
            return {"seeded": [], "preserved": [PROGRAM_CATALOG_KEY]}
        self._save({PROGRAM_CATALOG_KEY: _bootstrap_catalog()})
        return {"seeded": [PROGRAM_CATALOG_KEY], "preserved": []}

    def list_programs(self, *, include_inactive: bool = False) -> list[dict[str, Any]]:
        persisted = self._load((PROGRAM_CATALOG_KEY,))
        if PROGRAM_CATALOG_KEY not in persisted:
            return _bootstrap_catalog()
        catalog = normalize_program_catalog(persisted[PROGRAM_CATALOG_KEY])
        return catalog if include_inactive else [entry for entry in catalog if entry["active"]]

    def active_program_names(self) -> set[str]:
        return {entry["display_name"] for entry in self.list_programs()}

    def create_program(self, payload: object) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Program payload is required.")
        catalog = self.list_programs(include_inactive=True)
        entry = _catalog_entry(
            {
                "code": payload.get("code"),
                "display_name": payload.get("display_name"),
                "active": payload.get("active", True),
                "order": payload.get("order", max((item["order"] for item in catalog), default=0) + 1),
            },
            len(catalog),
        )
        self._save({PROGRAM_CATALOG_KEY: normalize_program_catalog([*catalog, entry])})
        return entry

    def update_program(self, code: str, payload: object) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Program payload is required.")
        code = _normalized_code(code)
        catalog = self.list_programs(include_inactive=True)
        for index, entry in enumerate(catalog):
            if entry["code"] != code:
                continue
            updated = _catalog_entry(
                {
                    **entry,
                    **{
                        key: value
                        for key, value in payload.items()
                        if key in {"display_name", "active", "order"}
                    },
                },
                index,
            )
            catalog[index] = updated
            self._save({PROGRAM_CATALOG_KEY: normalize_program_catalog(catalog)})
            return updated
        raise LookupError("Program not found.")


program_service = ProgramService()


__all__ = [
    "PROGRAM_CATALOG_KEY",
    "ProgramService",
    "normalize_program_catalog",
    "program_service",
]