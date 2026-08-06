from __future__ import annotations

import unittest

from backend.server.services.program_service import ProgramService


class ProgramServiceTests(unittest.TestCase):
    def _service(self, initial=None):  # type: ignore[no-untyped-def]
        store = dict(initial or {})

        def load(keys):  # type: ignore[no-untyped-def]
            return {key: store[key] for key in keys if key in store}

        def save(updates):  # type: ignore[no-untyped-def]
            store.update(updates)

        return ProgramService(load=load, save=save), store

    def test_seed_catalog_is_idempotent_and_active_by_default(self) -> None:
        service, store = self._service()

        first = service.seed_program_catalog()
        second = service.seed_program_catalog()

        self.assertEqual(first["seeded"], ["programCatalog"])
        self.assertEqual(second["seeded"], [])
        self.assertTrue(store["programCatalog"])
        self.assertTrue(all(item["active"] for item in service.list_programs()))

    def test_deactivated_program_remains_historical_but_not_active(self) -> None:
        service, _store = self._service()
        service.seed_program_catalog()
        program = service.list_programs()[0]

        service.update_program(program["code"], {"active": False})

        self.assertNotIn(program["display_name"], service.active_program_names())
        self.assertIn(
            program["display_name"],
            [item["display_name"] for item in service.list_programs(include_inactive=True)],
        )

    def test_create_rejects_duplicate_codes_and_names(self) -> None:
        service, _store = self._service()
        service.seed_program_catalog()
        existing = service.list_programs()[0]

        with self.assertRaisesRegex(ValueError, "unique"):
            service.create_program(
                {"code": existing["code"], "display_name": "A distinct program"}
            )
        with self.assertRaisesRegex(ValueError, "unique"):
            service.create_program(
                {"code": "DISTINCT", "display_name": existing["display_name"]}
            )