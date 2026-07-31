"""
Ollama Provider

Provides text generation using a locally hosted Ollama model.

CTRL4 Chatbot MK II

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from __future__ import annotations

import logging

import requests

from ..config import Config
from .base_provider import BaseProvider, LLMResponse

logger = logging.getLogger(__name__)


class OllamaProvider(BaseProvider):
    """
    Ollama implementation of the CTRL4 LLM Provider.
    """

    def __init__(self):

        self.config = Config()

        self.available = False

        self.initialization_error: str | None = None

        try:

            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=5,
            )

            if response.status_code == 200:

                self.available = True

                logger.info("OllamaProvider initialized successfully.")

            else:

                self.initialization_error = (
                    f"Ollama returned HTTP {response.status_code}"
                )

        except Exception as exception:

            self.initialization_error = str(exception)
            logger.exception(
                "Failed to initialize Ollama provider."
            )

    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:

        if not self.available:

            return LLMResponse(
                success=False,
                text="",
                error=(
                    self.initialization_error
                    or "Ollama is unavailable."
                ),
            )

        try:

            response = requests.post(

                self.config.OLLAMA_URL,

                json={

                    "model": self.config.OLLAMA_MODEL,

                    "prompt": prompt,

                    "stream": False,

                },

                timeout=120,

            )

            response.raise_for_status()

            data = response.json()

            return LLMResponse(

                success=True,

                text=data.get(
                    "response",
                    "",
                ).strip(),

            )

        except Exception as exception:

            logger.exception(
                "Ollama provider failed while generating a response using model '%s'.",
                self.config.OLLAMA_MODEL,
            )

            return LLMResponse(

                success=False,

                text="",

                error=str(exception),

            )

    def status(
        self,
    ) -> dict[str, object]:

        return {

            "provider": "ollama",

            "ready": self.available,

            "configured": True,

            "model": self.config.OLLAMA_MODEL,

            "error": self.initialization_error,

        }