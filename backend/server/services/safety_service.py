"""
Safety Service

Performs safety validation before and after AI generation.

Responsibilities

- Crisis Detection
- Diagnosis Detection
- Greeting Detection
- Acknowledgement Detection
- Escalation Decision

CTRL4 Chatbot MK III

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from __future__ import annotations

import re

from dataclasses import dataclass
from typing import Final


@dataclass
class SafetyResult:

    safe: bool

    should_escalate: bool

    response: str | None = None

    reason: str | None = None


class SafetyService:

    _CRISIS_RESPONSES: Final[dict[str, str]] = {
        "english": (
            "I'm really sorry you're going through this. "
            "Please contact the Guidance Office immediately "
            "or reach out to someone you trust. "
            "If you are in immediate danger, "
            "please contact your local emergency services."
        ),
        "filipino": (
            "Ikinalulungkot kong nararanasan mo ito. "
            "Mangyaring makipag-ugnayan agad sa Guidance Office "
            "o sa isang taong pinagkakatiwalaan mo. "
            "Kung nasa agarang panganib ka, "
            "tumawag sa lokal na emergency services."
        ),
        "taglish": (
            "I'm really sorry na nararanasan mo ito. "
            "Please contact the Guidance Office agad "
            "or reach out to someone you trust. "
            "Kung nasa immediate danger ka, "
            "please contact your local emergency services."
        ),
    }
    _DIAGNOSIS_RESPONSES: Final[dict[str, str]] = {
        "english": (
            "I'm not able to diagnose mental health conditions. "
            "I encourage you to speak with a licensed guidance "
            "counselor for proper support."
        ),
        "filipino": (
            "Hindi ako makakapagbigay ng diagnosis para sa kalusugang "
            "pangkaisipan. Hinihikayat kitang makipag-usap sa isang "
            "lisensyadong guidance counselor para sa angkop na suporta."
        ),
        "taglish": (
            "Hindi ako makakapagbigay ng mental health diagnosis. "
            "I encourage you to speak with a licensed guidance "
            "counselor for proper support."
        ),
    }

    CRISIS_PATTERNS: Final[tuple[str, ...]] = (

        # English
        r"\bkill me now\b",
        r"\bkill myself\b",
        r"\bsuicide\b",
        r"\bend my life\b",
        r"\b(?:i want to|i wanna|i(?:'m| am) going to|i(?:'m| am) gonna) "
        r"(?:hang|harm|hurt) myself\b",
        r"\b(?:i want to|i wanna|i(?:'m| am) going to|i(?:'m| am) gonna) "
        r"(?:use|grab|get) (?:a |the )?(?:gun|weapon)\b",
        r"\b(?:i want to|i wanna|i(?:'m| am) going to|i(?:'m| am) gonna) "
        r"jump(?:\s+off)?\b",
        r"\b(?:i want to|i wanna|i wish i could) finish my life\b",
        r"\b(?:i am|i'm) done with my life\b",
        r"\blife (?:is not|isn't) worth living\b",
        r"\blife (?:is not|isn't) worth it\b",
        r"\bwant to die\b",
        r"\bself harm\b",
        r"\bhurt myself\b",
        r"\bi (?:don't|do not) want to live(?: anymore)?\b",
        r"\bi (?:don't|do not) think i want to live(?: anymore)?\b",
        r"\bi (?:don't|do not) want to exist anymore\b",
        r"\bi can't do this anymore\b",
        r"\bi can't go on\b",
        r"\bi give up\b",
        r"\bi want to disappear\b",
        r"\bi wish i could disappear\b",
        r"\bi wish i was dead\b",
        r"\bi don't want to wake up\b",
        r"\bi wish i would not wake up\b",
        r"\bi am tired of living\b",
        r"\bnothing matters anymore\b",
        r"\beveryone would be better off without me\b",
        r"\bi want everything to end\b",
        r"\bi should end everything\b",
        r"\bi (?:don't|do not) see a reason to keep going\b",
        r"\b(?:i am|i'm) being abused\b",
        r"\b(?:someone|they) (?:is|are) hurting me\b",
        r"\b(?:i want to|going to) hurt (?:someone|them)\b",
        r"\b(?:i want to|going to) kill (?:someone|them)\b",
        r"\bi(?:'m| am) (?:going to|gonna) kill "
        r"(?:him|her|them|my (?:family|parents|partner|friend))\b",
        r"\bi killed someone\b",
        r"\bi (?:can't|cannot) promise (?:that )?i(?:'ll| will) be safe\b",
        r"\bdanger to (?:myself|others)\b",
        r"\bsevere depression\b",
        r"\bpanic attacks?\b",

        # Filipino / Taglish
        r"\bmagpapakamatay\b",
        r"\bayoko nang mabuhay\b",
        r"\bpapatayin ko ang sarili ko\b",
        r"\bsaktan ang sarili\b",
        r"\bhindi ko na kaya\b",
        r"\bgusto ko na(?:ng)? mawala\b",
        r"\bwala nang saysay\b",
        r"\bdi ko na kaya\b",
    )

    # These phrases are common expressions of academic frustration in
    # Filipino.  They become crisis evidence only with an additional explicit
    # self-harm, death, or loss-of-life signal; they are not safe to treat as
    # crisis evidence in isolation.
    AMBIGUOUS_FILIPINO_DISTRESS_PATTERNS: Final[tuple[str, ...]] = (
        r"\bsuko na ako\b",
        r"\bpagod na pagod na ako\b",
        r"\bayoko na\b",
    )
    HIGH_RISK_FILIPINO_CONTEXT_PATTERNS: Final[tuple[str, ...]] = (
        r"\b(?:magpapakamatay|magpakamatay|mamatay|papatayin|"
        r"saktan)\b",
        r"\b(?:sarili|mabuhay|mawala)\b",
    )

    DIAGNOSIS_PATTERNS: Final[tuple[str, ...]] = (

        r"\bdo i have depression\b",
        r"\bdo i have anxiety\b",
        r"\bam i depressed\b",
        r"\bdiagnose me\b",
        r"\bdo i have adhd\b",
        r"\bdo i have bipolar\b",
        r"\bdo i have ptsd\b",
        r"\bam i anxious\b",
        r"\bam i mentally ill\b",
        r"\bwhat mental illness do i have\b",

        r"\bmay depression ba ako\b",
        r"\bmay anxiety ba ako\b",
        r"\bdiagnose\b",
        r"\bmay adhd ba ako\b",
        r"\bmay bipolar ba ako\b",
        r"\bmay ptsd ba ako\b",
        r"\banong sakit ko\b",
    )

    GREETINGS: Final[frozenset[str]] = frozenset({
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "kumusta",
        "kamusta",
        "hello po",
        "hi po",
        "good day",
        "yo",
        "sup",
        "hola",
        "hiya",
        "hello there",
    })

    ACKNOWLEDGEMENTS: Final[frozenset[str]] = frozenset({
        "thanks",
        "thank you",
        "thank you so much",
        "salamat",
        "salamat po",
        "ok",
        "okay",
        "noted",
        "thanks po",
        "thank you po",
        "ty",
        "tysm",
        "sige",
        "copy",
        "got it",
        "understood",
        "okay po",
        "okay thanks",
        "salamat marami",
    })

    def check(
        self,
        message: str,
        language: str = "english",
    ) -> SafetyResult:

        # Normalize typographic apostrophes before matching deterministic
        # English contractions such as "can't" and "I'm".
        text = message.lower().strip().translate(str.maketrans({
            "’": "'",
            "‘": "'",
            "`": "'",
            "´": "'",
        }))

        if not text:
            return SafetyResult(
                safe=True,
                should_escalate=False,
            )

        if self._is_crisis(text):

            return SafetyResult(
                safe=False,
                should_escalate=True,
                reason="crisis",
                response=self._CRISIS_RESPONSES.get(
                    language.lower(),
                    self._CRISIS_RESPONSES["english"],
                ),
            )

        if self._asks_for_diagnosis(text):

            return SafetyResult(
                safe=False,
                should_escalate=True,
                reason="diagnosis",
                response=self._DIAGNOSIS_RESPONSES.get(
                    language.lower(),
                    self._DIAGNOSIS_RESPONSES["english"],
                ),
            )

        if self._is_greeting(text):

            return SafetyResult(
                safe=True,
                should_escalate=False,
                reason="greeting",
            )

        if self._is_acknowledgement(text):

            return SafetyResult(
                safe=True,
                should_escalate=False,
                reason="acknowledgement",
            )

        return SafetyResult(
            safe=True,
            should_escalate=False,
        )

    def _is_crisis(
        self,
        text: str,
    ) -> bool:

        if any(
            re.search(pattern, text)
            for pattern in self.CRISIS_PATTERNS
        ):
            return True

        ambiguous_distress_matches = sum(
            bool(re.search(pattern, text))
            for pattern in self.AMBIGUOUS_FILIPINO_DISTRESS_PATTERNS
        )
        if ambiguous_distress_matches >= 2:
            return True

        return (
            any(
                re.search(pattern, text)
                for pattern in self.AMBIGUOUS_FILIPINO_DISTRESS_PATTERNS
            )
            and any(
                re.search(pattern, text)
                for pattern in self.HIGH_RISK_FILIPINO_CONTEXT_PATTERNS
            )
        )

    def _asks_for_diagnosis(
        self,
        text: str,
    ) -> bool:

        return any(
            re.search(pattern, text)
            for pattern in self.DIAGNOSIS_PATTERNS
        )

    def _is_greeting(
        self,
        text: str,
    ) -> bool:

        return text in self.GREETINGS

    def _is_acknowledgement(
        self,
        text: str,
    ) -> bool:

        return text in self.ACKNOWLEDGEMENTS
