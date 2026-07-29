"""
Base LLM Provider

Defines the interface that every Large Language Model provider
(Gemini, Ollama, OpenRouter, etc.) must implement.

CTRL4 Chatbot MK II

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """
    Standard response returned by every LLM provider.
    """

    success: bool
    text: str
    error: str | None = None


class BaseProvider(ABC):
    """
    Abstract base class for all CTRL4 LLM providers.

    Every provider must implement the same interface so
    AIService never needs to know which LLM is being used.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:
        """
        Generate a response from the language model.
        """
        pass

    @abstractmethod
    def status(
        self,
    ) -> dict[str, object]:
        """
        Return provider status information.
        """
        pass