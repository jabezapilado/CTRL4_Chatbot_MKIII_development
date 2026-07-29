from __future__ import annotations

from enum import Enum


class ConversationTopic(str, Enum):

    GENERAL = "General"

    ACADEMICS = "Academics"

    RELATIONSHIPS = "Relationships"

    FAMILY = "Family"

    FRIENDSHIPS = "Friendships"

    MENTAL_HEALTH = "Mental Health"

    CAREER = "Career"

    GUIDANCE_OFFICE = "Guidance Office"

    PERSONAL_GROWTH = "Personal Growth"