"""
Gemini Provider

Provides text generation using Google's Gemini API.

CTRL4 Chatbot MK III

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from __future__ import annotations

import logging

import google.generativeai as genai

from ..config import Config
from .base_provider import BaseProvider, LLMResponse

logger = logging.getLogger(__name__)

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

            logger.warning(
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

            logger.info("GeminiProvider initialized successfully.")

        except Exception as exception:

            self.initialization_error = str(exception)

            logger.exception(
                "Failed to initialize Gemini provider."
            )

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

            response = self._generate_content(prompt)
            finish_reason = self._finish_reason(response)

            # Gemini can return syntactically valid but visibly unfinished text
            # when its candidate reaches the configured output limit.  Retry
            # once with a concise-completion instruction instead of showing a
            # student a sentence cut off mid-thought.  Do not append partial
            # generated text to the retry prompt.
            if self._needs_completion_retry(
                response,
                finish_reason,
                self.config.GEMINI_MAX_OUTPUT_TOKENS,
            ):
                logger.warning(
                    "Gemini response was incomplete; retrying once with a concise completion."
                )
                response = self._generate_content(
                    f"{prompt}\n\n"
                    "OUTPUT REQUIREMENT: Answer the student's full request. Return a "
                    "complete answer that ends on a finished sentence, not a comma, "
                    "colon, dash, or incomplete list item. Use at most 160 words and "
                    "two short paragraphs. Do not mention these instructions.",
                    max_output_tokens=max(
                        self.config.GEMINI_MAX_OUTPUT_TOKENS,
                        1536,
                    ),
                )
                finish_reason = self._finish_reason(response)

            if self._needs_completion_retry(
                response,
                finish_reason,
                max(
                    self.config.GEMINI_MAX_OUTPUT_TOKENS,
                    1536,
                ),
            ):
                logger.warning(
                    "Gemini response remained incomplete after the concise retry."
                )
                return LLMResponse(
                    success=False,
                    text="",
                    error="The language model reached its response length limit.",
                    finish_reason=finish_reason,
                )

            if response and response.text:

                return LLMResponse(
                    success=True,
                    text=response.text.strip(),
                    finish_reason=finish_reason,
                )

            logger.warning("Gemini returned an empty response.")

            return LLMResponse(
                success=False,
                text="",
                error="No response generated.",
                finish_reason=finish_reason,
            )

        except Exception as exception:

            logger.exception(
                "Gemini provider failed while generating a response using model '%s'.",
                self.config.GEMINI_MODEL,
            )

            return LLMResponse(
                success=False,
                text="",
                error=str(exception),
            )

    def _generate_content(
        self,
        prompt: str,
        *,
        max_output_tokens: int | None = None,
    ):
        return self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=self.config.GEMINI_TEMPERATURE,
                max_output_tokens=(
                    self.config.GEMINI_MAX_OUTPUT_TOKENS
                    if max_output_tokens is None
                    else max_output_tokens
                ),
            ),
        )

    @staticmethod
    def _finish_reason(response: object) -> str | None:
        candidates = getattr(response, "candidates", None)
        if not candidates:
            return None
        candidate = candidates[0]
        reason = getattr(candidate, "finish_reason", None)
        if reason is None:
            return None
        name = getattr(reason, "name", None)
        text = str(name or reason).strip()
        return text.upper() if text else None

    @staticmethod
    def _reached_output_limit(finish_reason: str | None) -> bool:
        return bool(
            finish_reason
            and (
                "MAX_TOKENS" in finish_reason
                or "MAX_TOKEN" in finish_reason
            )
        )

    @staticmethod
    def _candidate_token_count(response: object) -> int | None:
        """Return Gemini's generated-candidate token count when available.

        This metadata is a second signal for an output cap.  It matters when a
        provider returns a ``STOP`` label despite consuming its entire output
        budget.  The check is defensive because older Gemini SDK responses may
        not expose usage metadata.
        """
        usage_metadata = getattr(response, "usage_metadata", None)
        count = getattr(usage_metadata, "candidates_token_count", None)
        try:
            return int(count) if count is not None else None
        except (TypeError, ValueError):
            return None

    @classmethod
    def _needs_completion_retry(
        cls,
        response: object,
        finish_reason: str | None,
        output_token_limit: int,
    ) -> bool:
        """Detect a provider cutoff even when Gemini reports ``STOP``.

        Gemini normally uses ``MAX_TOKENS`` for a cutoff, but provider output
        can occasionally arrive as a syntactically successful candidate ending
        at a comma, colon, or dangling word.  A student must not see a partial
        response merely because the provider did not label that candidate as a
        token-limit finish.
        """
        if cls._reached_output_limit(finish_reason):
            return True

        # Treat a candidate that consumes the full configured budget as a
        # likely cutoff even if Gemini labels it STOP and it happens to finish
        # on punctuation.  Retrying from the original prompt prevents the
        # partial text from being exposed or fed back into the model.
        candidate_tokens = cls._candidate_token_count(response)
        if candidate_tokens is not None and candidate_tokens >= output_token_limit:
            return True

        text = str(getattr(response, "text", "") or "").strip()
        if not text:
            return False

        # Quotes and closing brackets may follow a complete sentence.  The
        # sentence-ending punctuation itself must still be present.
        terminal = text.rstrip("\\\"'”’)]}").rstrip()
        return bool(terminal) and terminal[-1] not in ".?!…"

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
