"""Regression coverage for Gemini generation configuration."""

from __future__ import annotations

import importlib
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT / "backend/server"
PROVIDERS_DIR = SERVER_DIR / "llm_providers"
PACKAGE = "gemini_provider_test.server.llm_providers"


class _GenerationConfig:
    def __init__(self, **values: object) -> None:
        self.values = values


class _Model:
    def __init__(self) -> None:
        self.calls: list[tuple[str, _GenerationConfig]] = []

    def generate_content(
        self,
        prompt: str,
        *,
        generation_config: _GenerationConfig,
    ) -> object:
        self.calls.append((prompt, generation_config))
        return types.SimpleNamespace(text="A grounded response.")


def _load_provider() -> tuple[type, _Model]:
    root_package = types.ModuleType("gemini_provider_test")
    root_package.__path__ = []
    server_package = types.ModuleType("gemini_provider_test.server")
    server_package.__path__ = [str(SERVER_DIR)]
    providers_package = types.ModuleType(PACKAGE)
    providers_package.__path__ = [str(PROVIDERS_DIR)]

    config = types.ModuleType("gemini_provider_test.server.config")
    config.Config = lambda: types.SimpleNamespace(
        GEMINI_API_KEY="test-key",
        GEMINI_MODEL="gemini-test",
        GEMINI_TEMPERATURE=0.45,
        GEMINI_MAX_OUTPUT_TOKENS=640,
    )

    model = _Model()
    generativeai = types.ModuleType("google.generativeai")
    generativeai.configure = lambda **_values: None
    generativeai.GenerativeModel = lambda **_values: model
    generativeai.GenerationConfig = _GenerationConfig
    google = types.ModuleType("google")
    google.__path__ = []
    google.generativeai = generativeai

    sys.modules[root_package.__name__] = root_package
    sys.modules[server_package.__name__] = server_package
    sys.modules[providers_package.__name__] = providers_package
    sys.modules[config.__name__] = config
    sys.modules[google.__name__] = google
    sys.modules[generativeai.__name__] = generativeai
    module = importlib.import_module(f"{PACKAGE}.gemini_provider")
    return module.GeminiProvider, model


class GeminiProviderConfigurationTests(unittest.TestCase):
    def test_applies_configured_temperature_and_output_limit(self) -> None:
        module_names = (
            "gemini_provider_test",
            "gemini_provider_test.server",
            PACKAGE,
            "gemini_provider_test.server.config",
            f"{PACKAGE}.gemini_provider",
            f"{PACKAGE}.base_provider",
            "google",
            "google.generativeai",
        )
        previous_modules = {name: sys.modules.get(name) for name in module_names}

        try:
            provider_class, model = _load_provider()
            result = provider_class().generate("Prompt")

            self.assertTrue(result.success)
            self.assertEqual(result.text, "A grounded response.")
            self.assertEqual(model.calls[0][0], "Prompt")
            self.assertEqual(
                model.calls[0][1].values,
                {"temperature": 0.45, "max_output_tokens": 640},
            )
        finally:
            for name, module in previous_modules.items():
                if module is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = module


if __name__ == "__main__":
    unittest.main()
