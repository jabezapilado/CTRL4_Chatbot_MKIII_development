from __future__ import annotations


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
        
        # -----------------------------------------
        # Common repeated phrases
        # -----------------------------------------

        empathy_phrases = [
            "it sounds like",
            "i understand",
            "i'm sorry you're going through",
            "that sounds difficult",
        ]

        introductions = [
            "i'm ctrl4",
            "i am ctrl4",
            "guidance office ai assistant",
        ]

        closings = [
            "take care",
            "i'm here if you need",
            "feel free to reach out",
        ]
        
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

            greetings = [
                "hello",
                "hi",
                "hi there",
                "hello there",
            ]

            if any(lower.startswith(g) for g in greetings):

                for message in conversation:
                    if message.get("role") == "assistant":
                        previous = message.get("content", "").lower()

                        if any(g in previous for g in greetings):
                            return (
                                False,
                                "Repeated greeting detected.",
                            )

        # -----------------------------------------
        # Repeated Empathy
        # -----------------------------------------

        for previous in assistant_history:

            for phrase in empathy_phrases:

                if phrase in lower and phrase in previous:

                    return (
                        False,
                        "Repeated empathy detected.",
                    )

        # -----------------------------------------
        # Repeated Introduction
        # -----------------------------------------

        for previous in assistant_history:

            for phrase in introductions:

                if phrase in lower and phrase in previous:

                    return (
                        False,
                        "Repeated introduction detected.",
                    )

        # -----------------------------------------
        # Repeated Closing
        # -----------------------------------------

        for previous in assistant_history:

            for phrase in closings:

                if phrase in lower and phrase in previous:

                    return (
                        False,
                        "Repeated closing detected.",
                    )

        return True, ""