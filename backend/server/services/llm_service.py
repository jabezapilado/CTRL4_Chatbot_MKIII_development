"""
LLM Service

Provides a unified interface for communicating with
different Large Language Model providers.

CTRL4 Chatbot MK II

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from __future__ import annotations

from ..config import Config
from ..llm_providers import (
    BaseProvider,
    GeminiProvider,
    OllamaProvider,
    LLMResponse,
)


class LLMService:
    """
    Unified interface for CTRL4's language models.

    AIService communicates only with this class.
    The actual provider is selected through the
    application configuration.
    """

    def __init__(self):

        self.config = Config()

        self.provider: BaseProvider

        provider_name = self.config.LLM_PROVIDER.lower()

        if provider_name == "ollama":

            self.provider = OllamaProvider()

        elif provider_name == "gemini":

            self.provider = GeminiProvider()

        else:

            raise ValueError(
                f"Unsupported LLM provider: {provider_name}"
            )

        print(
            f"LLMService using provider: {provider_name}"
        )

    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:

        return self.provider.generate(prompt)

    def status(
        self,
    ) -> dict[str, object]:

        return self.provider.status()