from __future__ import annotations

from dataclasses import dataclass
from .llm_service import LLMService

FLAGGED_RECOMMENDATION = (
    "Guidance Office follow-up is recommended."
)

NORMAL_RECOMMENDATION = (
    "No immediate intervention is required."
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

        summary_text = self._build_summary(
            conversation=conversation,
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
            primary_concern=topic,
            conversation_type="general",
            appointment_recommendation=flagged,
            recommendations=recommendation,
            suggested_intervention=recommendation,
            total_messages=len(conversation),
        )
    
    def _build_summary(
        self,
        *,
        conversation: list[dict],
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
        )

        try:
            return self.generate_text(prompt)

        except RuntimeError as error:
            # TODO: Log the error in a future version.
            return (
                "An automatic summary could not be generated for this "
                "conversation. Please review the conversation manually if "
                "it is still available."
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

        lines = []

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
    ) -> str:
        """
        Build the prompt used to summarize the conversation.
        """

        transcript = self._format_conversation(
            conversation=conversation,
        )

        return f"""\
        You are assisting the Holy Angel University Guidance Office.

        Your task is to generate a confidential conversation summary for Guidance personnel.

        Instructions:

        - Write only one paragraph.
        - Keep the summary between 100 and 150 words.
        - Focus on the student's primary concern.
        - Briefly describe the student's emotional state.
        - Briefly mention the guidance or support that was provided.
        - Do not invent, assume, or exaggerate information.
        - Do not diagnose any mental health condition.
        - Do not include greetings, introductions, or small talk.
        - Do not address the student directly.
        - Write in a professional, objective, third-person tone.

        Conversation Transcript:

        {transcript}
        """.strip()