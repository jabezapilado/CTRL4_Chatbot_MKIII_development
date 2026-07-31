from __future__ import annotations
from typing import Final


EMPATHY_PHRASES: Final[tuple[str, ...]] = (
    "it sounds like",
    "i understand",
    "i'm sorry you're going through",
    "that sounds difficult",
)

INTRODUCTION_PHRASES: Final[tuple[str, ...]] = (
    "i'm ctrl4",
    "i am ctrl4",
    "guidance office ai assistant",
)

CLOSING_PHRASES: Final[tuple[str, ...]] = (
    "take care",
    "i'm here if you need",
    "feel free to reach out",
)

GREETING_PHRASES: Final[tuple[str, ...]] = (
    "hello",
    "hi",
    "hi there",
    "hello there",
)


class ResponseValidator:

    def validate(
        self,
        response: str,
        conversation: list[dict],
    ) -> tuple[bool, str]:

        text = response.strip()

        # Empty response
        if not text:
            return False, "The response is empty."

        # Too short
        if len(text) < 15:
            return False, "The response is too short."

        lower = text.lower()
        
        assistant_history = []

        for message in conversation:

            role = message.get("role")

            if role is None and message.get("from") == "bot":
                role = "assistant"

            if role == "assistant":

                assistant_history.append(
                    message.get(
                        "content",
                        message.get("text", "")
                    ).lower()
                )

        # Don't greet again
        if conversation:

            if any(lower.startswith(g) for g in GREETING_PHRASES):

                for message in conversation:
                    if message.get("role") == "assistant":
                        previous = message.get("content", "").lower()

                        if any(g in previous for g in GREETING_PHRASES):
                            return (
                                False,
                                "Repeated greeting detected.",
                            )

        # -----------------------------------------
        # Repeated Empathy
        # -----------------------------------------

        for previous in assistant_history:

            for phrase in EMPATHY_PHRASES:

                if phrase in lower and phrase in previous:

                    return (
                        False,
                        "Repeated empathy detected.",
                    )

        # -----------------------------------------
        # Repeated Introduction
        # -----------------------------------------

        for previous in assistant_history:

            for phrase in INTRODUCTION_PHRASES:

                if phrase in lower and phrase in previous:

                    return (
                        False,
                        "Repeated introduction detected.",
                    )

        # -----------------------------------------
        # Repeated Closing
        # -----------------------------------------

        for previous in assistant_history:

            for phrase in CLOSING_PHRASES:

                if phrase in lower and phrase in previous:

                    return (
                        False,
                        "Repeated closing detected.",
                    )

        return True, ""