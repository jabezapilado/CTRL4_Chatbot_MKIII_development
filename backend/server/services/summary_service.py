from __future__ import annotations

from dataclasses import dataclass
from typing import Final
from .conversation_history import summary_conversation_evidence
from .llm_service import LLMService

FLAGGED_RECOMMENDATION: Final[str] = (
    "Guidance Office follow-up is recommended."
)

NORMAL_RECOMMENDATION: Final[str] = (
    "No escalation was required based on the recorded session."
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
            self._appointment_only_summary(appointment)
            if not evidence
            else self._build_summary(
                conversation=evidence,
                appointment=appointment,
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
    
    def _build_summary(
        self,
        *,
        conversation: list[dict],
        appointment: dict[str, str] | None,
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
            return self.generate_text(prompt)

        except RuntimeError:
            return (
                "An AI summary could not be generated from the recorded session."
            )

    @staticmethod
    def _appointment_only_summary(appointment: dict[str, str] | None) -> str:
        assert appointment is not None
        return (
            "The student submitted an appointment request regarding "
            f"{appointment['category']} for {appointment['preferred_date']} at "
            f"{appointment['preferred_time_slot']}. No additional chatbot "
            "conversation occurred during this session."
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

        - Write only one paragraph.
        - Keep the summary concise and no longer than the supplied facts require.
                - Focus on the student's primary concern.
                - Cover each distinct factual question and emotional concern expressed
                    by the student when both are present.
                - Mention emotion, guidance, support, or intervention only when it is
                    explicitly present in the supplied facts.
                - Do not invent, assume, or exaggerate information.
                - Use only facts explicitly present in the conversation transcript and
                    confirmed appointment request, if provided.
        - Do not diagnose any mental health condition.
        - Do not include greetings, introductions, or small talk.
        - Do not address the student directly.
        - Write in a professional, objective, third-person tone.

        Conversation Transcript:

        {transcript}
        {appointment_context}
        """.strip()

        return prompt