"""
Ollama Provider

Provides text generation using a locally hosted Ollama model.

CTRL4 Chatbot MK III

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from __future__ import annotations

import logging
from urllib.parse import urlsplit, urlunsplit

import requests

from ..config import Config
from .base_provider import BaseProvider, LLMResponse

logger = logging.getLogger(__name__)


def ollama_tags_url(generation_url: str) -> str:
    """Derive Ollama's tags endpoint from the configured generation URL."""
    parsed = urlsplit(str(generation_url).strip())
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("CHATBOT_OLLAMA_URL must be an absolute HTTP(S) URL.")

    path = parsed.path.rstrip("/")
    if path.endswith("/api/generate"):
        tags_path = f"{path[:-len('/generate')]}/tags"
    elif path.endswith("/api"):
        tags_path = f"{path}/tags"
    elif not path:
        tags_path = "/api/tags"
    else:
        tags_path = f"{path}/api/tags"

    return urlunsplit((parsed.scheme, parsed.netloc, tags_path, "", ""))


class OllamaProvider(BaseProvider):
    """
    Ollama implementation of the CTRL4 LLM Provider.
    """

    def __init__(self):

        self.config = Config()

        self.available = False

        self.initialization_error: str | None = None

        self.tags_url = ollama_tags_url(self.config.OLLAMA_URL)

        try:

            response = requests.get(
                self.tags_url,
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
