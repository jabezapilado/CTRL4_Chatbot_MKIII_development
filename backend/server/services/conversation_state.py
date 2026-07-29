from __future__ import annotations

from enum import Enum


class ConversationState(str, Enum):
    GREETING = "Greeting"

    EXPLORING = "Exploring Concern"

    EMOTIONAL_SUPPORT = "Providing Emotional Support"

    GUIDANCE_INFORMATION = "Providing Guidance Information"

    GENERAL = "General Conversation"

    CLOSING = "Closing Conversation"

    ANSWERING_PREVIOUS = "Answering Previous Question"

    ELABORATING = "Elaborating"

    TOPIC_CHANGE = "Topic Change"