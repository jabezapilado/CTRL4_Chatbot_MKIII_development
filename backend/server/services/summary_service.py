from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final
from .conversation_history import summary_conversation_evidence
from .llm_service import LLMService

FLAGGED_RECOMMENDATION: Final[str] = (
    "Immediate Guidance Office review is recommended. Assess the student's immediate "
    "safety, follow the approved Guidance Office protocol, and document the action taken."
)

NORMAL_RECOMMENDATION: Final[str] = (
    "No escalation was required based on the recorded session."
)
_UNSUPPORTED_SUMMARY_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"[\"`]") ,
    re.compile(
        r"\b(?:agreed|accepted help|accepted counseling|willing to|"
        r"was willing|committed to|intends to commit suicide|is suicidal)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:hotline|phone number|system prompt|internal prompt)\b", re.IGNORECASE),
    re.compile(r"\b(?:\+?\d[\d\s-]{6,}\d)\b"),
)

@dataclass
class ConversationSummary:
    """
    Structured summary generated after a conversation ends.
    """

    student_name: str
    topic: str
    language: str
    emotion: str
    flagged: bool
    summary: str
    recommendation: str
    primary_concern: str
    conversation_type: str
    appointment_recommendation: bool
    recommendations: str
    suggested_intervention: str
    total_messages: int


class SummaryService:
    """
    Generates a structured summary after a conversation ends.

    Responsibilities:
    - Generate a concise conversation summary
    - Store summary metadata
    - Provide counselor recommendations

    This service DOES NOT:
    - Save to the database
    - Delete conversations
    - Notify Guidance Office staff
    - Send emails
    """

    def __init__(
        self,
        llm: LLMService,
    ):
        self.llm = llm

    def generate_text(
        self,
        prompt: str,
    ) -> str:
        """
        Generate summary text using the configured language model.

        Parameters
        ----------
        prompt:
            The summarization prompt.

        Returns
        -------
        str
            The generated summary.

        Raises
        ------
        RuntimeError
            If the language model fails to generate a summary.
        """

        result = self.llm.generate(prompt)

        if not result.success:
            raise RuntimeError(
                result.error
                or "The language model failed to generate a summary."
            )

        return result.text
    
    def generate_summary(
        self,
        *,
        student_name: str,
        conversation: list[dict],
        topic: str,
        language: str,
        emotion: str,
        flagged: bool,
        appointment: dict[str, str] | None = None,
    ) -> ConversationSummary:
        """
        Generate a structured conversation summary.

        Parameters
        ----------
        student_name:
            Student's name.

        conversation:
            Complete conversation history.

        topic:
            Primary detected conversation topic.

        language:
            Detected language.

        emotion:
            Overall detected emotion.

        flagged:
            Whether the conversation has been flagged.

        Returns
        -------
        ConversationSummary
        """

        evidence = summary_conversation_evidence(conversation)
        if not evidence and appointment is None:
            raise ValueError("A summary requires student-authored evidence.")

        summary_text = (
            self._crisis_summary()
            if flagged and str(topic).strip().casefold() == "crisis concern"
            else self._appointment_only_summary(appointment)
            if not evidence
            else self._build_summary(
                conversation=evidence,
                appointment=appointment,
                flagged=flagged,
            )
        )

        recommendation = self._build_recommendation(
            flagged=flagged,
        )

        return ConversationSummary(
            student_name=student_name,
            topic=topic,
            language=language,
            emotion=emotion,
            flagged=flagged,
            summary=summary_text,
            recommendation=recommendation,
            primary_concern=(
                appointment["category"] if not evidence and appointment else topic
            ),
            conversation_type="appointment" if not evidence else "general",
            appointment_recommendation=bool(appointment),
            recommendations=recommendation,
            suggested_intervention=recommendation,
            total_messages=len(evidence),
        )

    def refresh_open_case_summary(
        self,
        *,
        prior_summary: object,
        conversation: list[dict],
    ) -> str:
        """Refresh an open case from its prior abstract summary and new evidence."""
        evidence = summary_conversation_evidence(conversation)
        prior = " ".join(str(prior_summary or "").split())
        if not evidence:
            return prior

        prompt = self._build_open_case_prompt(prior, evidence)
        try:
            generated = self.generate_text(prompt)
            refreshed = self._conservative_generated_summary(generated, flagged=True)
            return prior if refreshed.startswith("A conservative summary") else refreshed
        except RuntimeError:
            return prior
    
    def _build_summary(
        self,
        *,
        conversation: list[dict],
        appointment: dict[str, str] | None,
        flagged: bool,
    ) -> str:
        """
        Build the conversation summary.

        The actual AI-generated summary will be implemented
        in a later step.

        Parameters
        ----------
        conversation:
            Complete conversation history.

        Returns
        -------
        str
            Generated summary text.
        """

        prompt = self._build_prompt(
            conversation=conversation,
            appointment=appointment,
        )

        try:
            generated = self.generate_text(prompt)
            return self._conservative_generated_summary(generated, flagged=flagged)

        except RuntimeError:
            return (
                "An AI summary could not be generated from the recorded session."
            )

    @staticmethod
    def _conservative_generated_summary(text: object, *, flagged: bool) -> str:
        """Keep provider summaries abstract, factual, and appropriately brief."""
        summary = " ".join(str(text or "").split())
        if not summary or any(pattern.search(summary) for pattern in _UNSUPPORTED_SUMMARY_PATTERNS):
            return "A conservative summary could not be generated from the recorded session."

        sentences = re.split(r"(?<=[.!?])\s+", summary)
        maximum_sentences = 2 if flagged else 1
        return " ".join(sentences[:maximum_sentences])

    @staticmethod
    def _appointment_only_summary(appointment: dict[str, str] | None) -> str:
        assert appointment is not None
        return (
            "The student submitted an appointment request regarding "
            f"{appointment['category']} for {appointment['preferred_date']} at "
            f"{appointment['preferred_time_slot']}. No additional chatbot "
            "conversation occurred during this session."
        )

    @staticmethod
    def _crisis_summary() -> str:
        return (
            "The student expressed suicidal ideation or other high-risk safety "
            "concerns. The assistant provided an immediate safety response, and the "
            "conversation was referred to the Guidance Office for urgent review."
        )
    
    def _build_recommendation(
        self,
        *,
        flagged: bool,
    ) -> str:
        """
        Generate the counselor recommendation.
        """

        if flagged:
            return FLAGGED_RECOMMENDATION

        return NORMAL_RECOMMENDATION
    
    def _format_conversation(
        self,
        *,
        conversation: list[dict],
    ) -> str:
        """
        Convert the conversation history into a formatted
        transcript suitable for summarization.
        """

        lines: list[str] = []

        for message in conversation:

            role = message.get(
                "role",
                message.get("from", "user"),
            )
            
            if role in ("assistant", "bot"):
                role = "Assistant"
            else:
                role = "Student"

            text = message.get(
                "content",
                message.get("text", ""),
            )
            
            if not text.strip():
                continue

            lines.append(
                f"{role}: {text}"
            )

        return "\n".join(lines)
    
    def _build_prompt(
        self,
        *,
        conversation: list[dict],
        appointment: dict[str, str] | None,
    ) -> str:
        """
        Build the prompt used to summarize the conversation.
        """

        transcript = self._format_conversation(
            conversation=conversation,
        )

        appointment_context = ""
        if appointment is not None:
            appointment_context = (
                "\n\nConfirmed Appointment Request:\n"
                f"Category: {appointment['category']}\n"
                f"Preferred date: {appointment['preferred_date']}\n"
                f"Preferred time: {appointment['preferred_time_slot']}"
            )

        prompt = f"""\
        You are assisting the Holy Angel University Guidance Office.

        Your task is to generate a confidential conversation summary for Guidance personnel.

        Instructions:

                - Write one abstract, professional paragraph with no quotations.
                - Routine summaries must be one sentence. Mixed and high-risk summaries
                    may use two sentences, but never more.
                - Preserve chronology: describe a student request or concern before the
                    assistant action that followed it.
                - Cover each distinct factual question and emotional concern when both
                    are present.
                - Describe only observable facts from the supplied conversation and
                    confirmed appointment request, if provided.
                - Do not infer agreement, willingness, acceptance of help, intent,
                    diagnosis, counseling history, or future behavior.
                - Use cautious language such as "expressed", "reported", "requested",
                    and "replied" rather than certainty about internal state.
                - Mention an assistant action only when it is material: appointment
                    guidance for a routine appointment request, or an immediate safety
                    response and Guidance Office referral for high-risk safety handling.
                - Never include message quotations, a transcript, phone numbers, hotline
                    text, internal prompts, IDs, or internal configuration.
                - Do not invent, assume, or exaggerate information.
        - Do not diagnose any mental health condition.
        - Do not include greetings, introductions, or small talk.
        - Do not address the student directly.
        - Write in a professional, objective, third-person tone.

        Conversation Transcript:

        {transcript}
        {appointment_context}
        """.strip()

        return prompt

    def _build_open_case_prompt(
        self,
        prior_summary: str,
        conversation: list[dict],
    ) -> str:
        transcript = self._format_conversation(conversation=conversation)
        return f"""\
        You are assisting the Holy Angel University Guidance Office.

        Update an existing open case summary using the prior abstract summary and
        the new conversation evidence below. Write no more than two factual,
        professional sentences. Retain the prior safety concern, preserve
        chronology, and describe the new student message only as an observable
        follow-up. Do not quote messages, infer agreement or future behavior,
        include phone numbers, or expose a transcript.

        Prior Abstract Summary:
        {prior_summary}

        New Conversation Evidence:
        {transcript}
        """.strip()