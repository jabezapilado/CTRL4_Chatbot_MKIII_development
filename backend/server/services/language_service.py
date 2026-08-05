"""
Language Service

Detects the language of a student's message.

Supported Languages
- English
- Filipino
- Taglish
- Unknown

CTRL4 Chatbot MK III

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

import re
from dataclasses import dataclass
from typing import Final


FILIPINO_WORDS: Final = {
    # Common words
    "ako",
    "ikaw",
    "siya",
    "kami",
    "kami",
    "kayo",
    "sila",
    "natin",
    "namin",
    "nila",

    "ang",
    "ng",
    "sa",
    "para",
    "lang",
    "kasi",
    "naman",
    "nga",
    "din",
    "rin",
    "pa",
    "po",
    "opo",
    "pwede",
    "maaari",
    "bakit",
    "kamusta",
    "kumusta",
    "gusto",
    "ayoko",
    "salamat",
    "musta",

    # School
    "eskwela",
    "paaralan",
    "pag-aaral",
    "aral",
    "klase",
    "guro",
    "propesor",
    "thesis",
    "exam",

    # Guidance
    "gabay",
    "guidance",
    "counselor",
    "appointment",

    # Emotions
    "pagod",
    "nahihirapan",
    "nahihiya",
    "naiiyak",
    "nalulungkot",
    "natatakot",
    "kabado",
    "nalilito",
    "problema",
    "stress",
    "burnout",

    # Family
    "magulang",
    "nanay",
    "tatay",
    "ate",
    "kuya",
    "kapatid",
    "kaibigan",
    "pamilya",
    "relasyon",
}


ENGLISH_WORDS: Final = {
    # Academic
    "school",
    "university",
    "college",
    "class",
    "classes",
    "course",
    "semester",
    "student",
    "teacher",
    "professor",
    "assignment",
    "activity",
    "project",
    "research",
    "paper",
    "thesis",
    "defense",
    "presentation",
    "exam",
    "quiz",
    "deadline",
    "grades",
    "study",
    "studying",

    # Guidance / Counseling
    "guidance",
    "counselor",
    "appointment",
    "session",
    "office",
    "help",
    "support",
    "advice",
    "career",
    "future",

    # Emotions
    "stress",
    "stressed",
    "pressure",
    "burnout",
    "burned",
    "overwhelmed",
    "sad",
    "happy",
    "worried",
    "anxiety",
    "anxious",
    "lonely",
    "alone",
    "tired",
    "confused",
    "afraid",
    "fear",
    "angry",
    "upset",

    # Daily conversation
    "today",
    "tomorrow",
    "yesterday",
    "really",
    "actually",
    "maybe",
    "probably",
    "because",
    "please",
    "thank",
    "thanks",
    "hello",
    "hi",
    "hey",
    "good",
    "morning",
    "afternoon",
    "evening",
    "feel",
    "feeling",
    "think",
    "understand",
    "understanding",
    "talk",
    "chat",
    "message",
}

CHAT_EXPRESSIONS: Final = {
    "haha",
    "hahaha",
    "hehe",
    "hehehe",
    "hmm",
    "hm",
    "ah",
    "aw",
    "oh",
    "ok",
    "okay",
    "yes",
    "no",
    "yup",
    "nope",
    "sure",
}

# Vocabulary shared by the English and Filipino lexicons is neutral evidence.
# A shared academic or guidance term alone must not make a message Taglish.
SHARED_VOCABULARY: Final = frozenset(FILIPINO_WORDS & ENGLISH_WORDS)


@dataclass
class LanguagePrediction:

    language: str
    confidence: float


class LanguageService:

    def detect(self, text: str) -> LanguagePrediction:
        
        # -----------------------------------------
        # Normalize Input
        # -----------------------------------------

        text = text.strip()
        if not text:
            return LanguagePrediction(
                language="unknown",
                confidence=0.0,
            )
        words = re.findall(r"\b[\w']+\b", text.lower())
        # -----------------------------------------
        # Short Chat Messages
        # -----------------------------------------
        if len(words) == 1 and words[0] in CHAT_EXPRESSIONS:
            return LanguagePrediction(
                language="english",
                confidence=0.60,
            )
        if not words:
            # -----------------------------------------
            # Emoji-only Messages
            # -----------------------------------------
            emoji_only = not re.search(r"[A-Za-zÀ-ÿ]", text)
            if emoji_only:
                return LanguagePrediction(
                    language="english",
                    confidence=0.50,
                )
            return LanguagePrediction(
                language="unknown",
                confidence=0.0,
            )
        # -----------------------------------------
        # Strong Language Indicators
        # -----------------------------------------

        english_indicators = {
            "the",
            "and",
            "because",
            "would",
            "could",
            "should",
            "please",
            "really",
            "actually",
        }

        filipino_indicators = {
            "ako",
            "ikaw",
            "siya",
            "kami",
            "kayo",
            "sila",
            "kasi",
            "lang",
            "naman",
            "nga",
            "din",
            "rin",
            "po",
            "opo",
        }

        filipino_count = 0
        english_count = 0

        for word in words:

            # Regular vocabulary. Shared words are intentionally neutral so
            # only language-exclusive vocabulary can establish mixed input.
            if word in FILIPINO_WORDS and word not in SHARED_VOCABULARY:
                filipino_count += 1

            if word in ENGLISH_WORDS and word not in SHARED_VOCABULARY:
                english_count += 1

            # Strong indicators
            if word in filipino_indicators:
                filipino_count += 2

            if word in english_indicators:
                english_count += 2

        total = filipino_count + english_count

        if total == 0:

            return LanguagePrediction(
                language="english",
                confidence=0.50,
            )

        filipino_ratio = filipino_count / total
        english_ratio = english_count / total

        # -----------------------------------------
        # Strong Taglish Detection
        # -----------------------------------------

        if english_count >= 1 and filipino_count >= 1:

            return LanguagePrediction(
                language="taglish",
                confidence=max(
                    english_ratio,
                    filipino_ratio,
                ),
            )

        # -----------------------------------------
        # English
        # -----------------------------------------

        if english_count > filipino_count:

            return LanguagePrediction(
                language="english",
                confidence=english_ratio,
            )

        # -----------------------------------------
        # Filipino
        # -----------------------------------------

        if filipino_count > english_count:

            return LanguagePrediction(
                language="filipino",
                confidence=filipino_ratio,
            )

        # -----------------------------------------
        # Default
        # -----------------------------------------

        return LanguagePrediction(
            language="english",
            confidence=0.50,
        )
