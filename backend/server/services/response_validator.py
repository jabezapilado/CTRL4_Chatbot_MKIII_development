from __future__ import annotations

from .conversation_history import normalize_conversation_history


class ResponseValidator:
    """Reject unusable output and known unhelpful canned deflections.

    ResponseSafetyService remains responsible for validating unsafe generated
    content. This guard deliberately keeps ordinary empathetic wording valid;
    it only rejects empty, malformed, exact repeated, or known generic
    deflections that do not help a student continue the conversation.
    """

    _GENERIC_DEFLECTIONS = (
        "i can't confirm that information",
        "i cannot confirm that information",
        "i don't want to make assumptions about what you're going through",
        "i do not want to make assumptions about what you're going through",
    )

    def validate(
        self,
        response: str,
        conversation: list[dict],
    ) -> tuple[bool, str]:

        if not isinstance(response, str):
            return False, "The response is malformed."

        text = response.strip()

        # Empty response
        if not text:
            return False, "The response is empty."

        # Too short
        if len(text) < 15:
            return False, "The response is too short."

        candidate = " ".join(text.casefold().split())

        if any(candidate.startswith(phrase) for phrase in self._GENERIC_DEFLECTIONS):
            return False, "Generic deflection detected."

        for message in normalize_conversation_history(conversation):
            if message["role"] != "assistant":
                continue
            previous = " ".join(message["content"].casefold().split())
            if previous == candidate:
                return False, "Repeated response detected."

        return True, ""
