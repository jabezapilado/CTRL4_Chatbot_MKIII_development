"""
Gemini Provider

Provides text generation using Google's Gemini API.

CTRL4 Chatbot MK II

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from __future__ import annotations

import google.generativeai as genai

from ..config import Config
from .base_provider import BaseProvider, LLMResponse


class GeminiProvider(BaseProvider):
    """
    Google Gemini implementation of the CTRL4 LLM Provider.

    This provider is responsible only for communicating with
    the Gemini API.

    Every LLM provider (Gemini, Ollama, OpenRouter, etc.)
    should expose the same interface.
    """

    def __init__(self):

        self.config = Config()

        self.available = False

        self.model: genai.GenerativeModel | None = None

        self.initialization_error: str | None = None

        if not self.config.GEMINI_API_KEY:

            self.initialization_error = (
                "Gemini API key is not configured."
            )

            print(
                "GeminiProvider: No API key configured. Gemini is disabled."
            )

            return

        try:

            genai.configure(
                api_key=self.config.GEMINI_API_KEY
            )

            self.model = genai.GenerativeModel(
                model_name=self.config.GEMINI_MODEL
            )

            self.available = True

            print(
                "GeminiProvider initialized successfully."
            )

        except Exception as exception:

            self.initialization_error = str(exception)

            print("=" * 60)
            print("Gemini Provider Initialization Error")
            print("=" * 60)
            print(exception)
            print("=" * 60)

            self.available = False

            self.model = None

    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:

        if not self.available or self.model is None:

            return LLMResponse(
                success=False,
                text="",
                error=(
                    self.initialization_error
                    or "Gemini provider is unavailable."
                ),
            )

        try:

            response = self.model.generate_content(prompt)

            if response and response.text:

                return LLMResponse(
                    success=True,
                    text=response.text.strip(),
                )

            print("=" * 60)
            print("Gemini returned an empty response.")
            print("=" * 60)

            return LLMResponse(
                success=False,
                text="",
                error="No response generated.",
            )

        except Exception as exception:

            print("=" * 60)
            print("Gemini Provider Exception")
            print("=" * 60)
            print(f"Model : {self.config.GEMINI_MODEL}")
            print(f"Error : {exception}")
            print("=" * 60)

            return LLMResponse(
                success=False,
                text="",
                error=str(exception),
            )

    def status(self) -> dict[str, object]:

        return {

            "provider": "gemini",

            "ready": self.available,

            "configured": bool(
                self.config.GEMINI_API_KEY
            ),

            "model": self.config.GEMINI_MODEL,

            "error": self.initialization_error,

        }