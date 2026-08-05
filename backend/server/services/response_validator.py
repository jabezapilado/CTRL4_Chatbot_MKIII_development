from __future__ import annotations
from .conversation_history import normalize_conversation_history


class ResponseValidator:
    """Reject unusable output, not ordinary natural language.

    ResponseSafetyService remains responsible for validating unsafe generated
    content.  This guard only protects against empty, malformed, or exact
    repeated responses, so common empathetic wording can remain conversational.
    """

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
        for message in normalize_conversation_history(conversation):
            if message["role"] != "assistant":
                continue
            previous = " ".join(message["content"].casefold().split())
            if previous == candidate:
                return False, "Repeated response detected."

        return True, ""
