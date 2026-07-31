"""
AI Service

Main AI orchestration service for CTRL4 Chatbot MK2.

Responsibilities

- Safety Validation
- Language Detection
- Emotion Detection
- Knowledge Retrieval (RAG)
- Prompt Construction
- LLM Response Generation

CTRL4 Chatbot MK2

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from __future__ import annotations
import logging
import time

from dataclasses import dataclass

from .emotion_service import EmotionService
from .language_service import LanguageService
from .rag_service import RAGService
from .prompt_builder import PromptBuilder, PromptInput
from .llm_service import LLMService
from .safety_service import SafetyService
from .conversation_state import ConversationState
from .conversation_topic import ConversationTopic
from .response_validator import ResponseValidator

logger = logging.getLogger(__name__)



@dataclass
class ChatResponse:

    success: bool

    response: str

    emotion: str

    sentiment: str

    language: str

    topic: str

    state: str

    escalated: bool

    confidence: float


class AIService:

    def __init__(
        self,
        safety: SafetyService | None = None,
        language: LanguageService | None = None,
        emotion: EmotionService | None = None,
        rag: RAGService | None = None,
        prompt_builder: PromptBuilder | None = None,
        llm: LLMService | None = None,
    ):

        self.safety = safety or SafetyService()

        self.language = language or LanguageService()

        self.emotion = emotion or EmotionService()

        self.rag = rag or RAGService()

        self.prompt_builder = prompt_builder or PromptBuilder()

        self.llm = llm or LLMService()
        
        self.response_validator = ResponseValidator()
    
    def generate_text(
        self,
        prompt: str,
    ) -> str:
        """
        Generate raw text from the configured LLM.
        This helper centralizes all communication with the
        configured language model.

        Parameters
        ----------
        prompt:
            The prompt sent to the language model.

        Returns
        -------
        str
            The generated response.

        Raises
        ------
        RuntimeError
            If the configured language model fails to generate a response.

        """

        llm = self.llm.generate(prompt)

        if not llm.success:
            raise RuntimeError(
                llm.error or
                "The language model failed to generate a response."
            )

        return llm.text

    def should_use_rag(
        self,
        message: str,
    ) -> bool:

        message = message.lower()

        GUIDANCE_KEYWORDS = (
            "guidance",
            "guidance office",
            "counselor",
            "counsellor",
            "appointment",
            "schedule",
            "office",
            "office hours",
            "referral",
            "consultation",
            "career counseling",
            "psychological assessment",
            "mental health program",
            "service",
            "services",
            "policy",
            "policies",
            "contact",
            "email",
            "facebook",
            "location",
            "room",
            "sjh",
            "hannah",
            "ryan",
        )

        return any(
            keyword in message 
            for keyword in GUIDANCE_KEYWORDS
        )

    def detect_conversation_state(
        self,
        message: str,
        conversation: list[dict],
    ) -> ConversationState:

        message_lower = message.lower()

        last_assistant = ""
        
        assistant_asked_question = False

        for item in reversed(conversation):

            if item.get("from") == "bot" or item.get("role") == "assistant":

                last_assistant = item.get(
                    "text",
                    item.get("content", "")
                ).lower()

                assistant_asked_question = (
                    last_assistant.strip().endswith("?")
                )

                break

        GREETINGS = (
            "hi",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
        )

        CLOSINGS = (
            "bye",
            "goodbye",
            "see you",
            "thank you",
            "thanks",
        )

        GUIDANCE = (
            "guidance",
            "guidance office",
            "counselor",
            "appointment",
            "office",
            "schedule",
            "services",
            "referral",
        )

        EMOTIONS = (
            "sad",
            "stress",
            "stressed",
            "burnout",
            "tired",
            "lonely",
            "alone",
            "worried",
            "anxious",
            "overwhelmed",
        )
        
        # -----------------------------------------
        # Reply Analysis
        # -----------------------------------------
        
        ACKNOWLEDGEMENT_RESPONSES = (
            "yes",
            "yeah",
            "yup",
            "no",
            "nope",
            "okay",
            "ok",
            "sure",
            "maybe",
            "i see",
            "thank you",
            "thanks",
        )

        if any(word in message_lower for word in CLOSINGS):
            return ConversationState.CLOSING

        if len(conversation) <= 1 and any(word in message_lower for word in GREETINGS):
            return ConversationState.GREETING
        
        # -----------------------------------------
        # Student Answered Previous Question
        # -----------------------------------------

        if (
            assistant_asked_question
            and message_lower.strip() in ACKNOWLEDGEMENT_RESPONSES
        ):
            return ConversationState.ANSWERING_PREVIOUS
        
        # -----------------------------------------
        # Student is Elaborating
        # -----------------------------------------

        if (
            assistant_asked_question
            and len(message_lower.split()) > 15
        ):
            return ConversationState.ELABORATING

        if any(word in message_lower for word in GUIDANCE):
            return ConversationState.GUIDANCE_INFORMATION

        # -----------------------------------------
        # Student is Exploring Their Concern
        # -----------------------------------------

        EXPLORING_KEYWORDS = (
            "because",
            "it's because",
            "i feel",
            "i've been",
            "i have been",
            "lately",
            "recently",
            "my problem",
            "the reason",
            "i think",
        )

        if (
            assistant_asked_question
            and any(
                keyword in message_lower
                for keyword in EXPLORING_KEYWORDS
            )
        ):
            return ConversationState.EXPLORING

        if any(word in message_lower for word in EMOTIONS):
            return ConversationState.EMOTIONAL_SUPPORT

        return ConversationState.GENERAL
    
    def detect_conversation_topic(
        self,
        message: str,
    ) -> ConversationTopic:

        message = message.lower()

        ACADEMICS = (
            "school",
            "class",
            "grades",
            "grade",
            "exam",
            "exams",
            "quiz",
            "study",
            "studying",
            "academic",
            "academics",
            "assignment",
            "project",
            "research",
            "thesis",
            "deadline",
            "deadlines",
            "cram",
            "cramming",
            "productivity",
            "productive",
            "motivation",
            "motivated",
            "time management",
            "procrastinate",
            "procrastinating",
            "subject",
            "professor",
            "teacher",
            "study tips",
            "exam preparation",
            "focus",
            "concentration",
            "learning",
            "learning style",
        )

        RELATIONSHIPS = (
            "boyfriend",
            "girlfriend",
            "relationship",
            "breakup",
            "partner",
            "dating",
            "love",
        )

        FAMILY = (
            "family",
            "mother",
            "father",
            "mom",
            "dad",
            "parents",
        )

        FRIENDSHIPS = (
            "friend",
            "friends",
            "classmate",
            "peer",
        )

        CAREER = (
            "career",
            "job",
            "work",
            "internship",
        )

        GUIDANCE = (
            "guidance",
            "counselor",
            "appointment",
            "office",
        )

        if any(word in message for word in GUIDANCE):
            return ConversationTopic.GUIDANCE_OFFICE

        if any(word in message for word in ACADEMICS):
            return ConversationTopic.ACADEMICS

        if any(word in message for word in RELATIONSHIPS):
            return ConversationTopic.RELATIONSHIPS

        if any(word in message for word in FAMILY):
            return ConversationTopic.FAMILY

        if any(word in message for word in FRIENDSHIPS):
            return ConversationTopic.FRIENDSHIPS

        if any(word in message for word in CAREER):
            return ConversationTopic.CAREER

        return ConversationTopic.GENERAL
    
    def respond(
        self,
        message: str,
        conversation: list[dict] | None = None,
    ) -> ChatResponse:

        if conversation is None:
            conversation = []
        
        # -----------------------------------------
        # Performance Tracking
        # -----------------------------------------

        pipeline_start = time.perf_counter()
        
        # Initialize pipeline timings
        safety_time = 0.0
        language_time = 0.0
        emotion_time = 0.0
        rag_time = 0.0
        prompt_time = 0.0
        llm_time = 0.0

        def print_pipeline_metrics():
            total_time = time.perf_counter() - pipeline_start
            logger.debug(
                "Pipeline timings | safety=%.3fs language=%.3fs emotion=%.3fs rag=%.3fs prompt=%.3fs llm=%.3fs total=%.3fs",
                safety_time,
                language_time,
                emotion_time,
                rag_time,
                prompt_time,
                llm_time,
                total_time,
            )
            
        try:

            # -----------------------------------------
            # Safety Validation
            # -----------------------------------------

            safety_start = time.perf_counter()
            safety = self.safety.check(message)
            safety_time = time.perf_counter() - safety_start

            if safety.response:

                return ChatResponse(
                    success=True,
                    response=safety.response,
                    emotion="Unknown",
                    sentiment="Unknown",
                    language="Unknown",
                    topic="Unknown",
                    state="Unknown",
                    escalated=safety.should_escalate,
                    confidence=0.0,
                )

            # -----------------------------------------
            # Language Detection
            # -----------------------------------------

            language_start = time.perf_counter()
            language = self.language.detect(message)
            language_time = time.perf_counter() - language_start

            # -----------------------------------------
            # Emotion Detection
            # -----------------------------------------

            emotion_start = time.perf_counter()
            emotion = self.emotion.predict(message)
            emotion_time = time.perf_counter() - emotion_start

            # -----------------------------------------
            # Conversation State
            # -----------------------------------------

            conversation_state = self.detect_conversation_state(
                message,
                conversation,
            )
            
            # -----------------------------------------
            # Conversation Topic
            # -----------------------------------------

            conversation_topic = self.detect_conversation_topic(
                message,
            )
            
            logger.debug(
                "Conversation classified | state=%s topic=%s message=%r",
                conversation_state.value,
                conversation_topic.value,
                message,
            )

            # -----------------------------------------
            # Knowledge Retrieval
            # -----------------------------------------

            rag_start = time.perf_counter()

            documents = []

            if self.rag.ready and self.should_use_rag(message):
                documents = self.rag.retrieve(message)

            rag_time = time.perf_counter() - rag_start

            # -----------------------------------------
            # Prompt Construction
            # -----------------------------------------

            prompt_start = time.perf_counter()
            prompt = self.prompt_builder.build(

                PromptInput(

                    message=message,

                    conversation=conversation,

                    emotion=emotion,

                    language=language,
                    
                    conversation_state=conversation_state.value,
                    
                    conversation_topic=conversation_topic.value,

                    documents=documents,
                )

            )
            prompt_time = time.perf_counter() - prompt_start

            # -----------------------------------------
            # LLM Response Generation
            # -----------------------------------------

            llm_start = time.perf_counter()
            llm_text = self.generate_text(prompt)
            llm_time = time.perf_counter() - llm_start

            # -----------------------------------------
            # Response Validation
            # -----------------------------------------

            valid, reason = self.response_validator.validate(
                llm_text,
                conversation,
            )

            if not valid:
                logger.debug(
                    "Response validation failed: %s",
                    reason,
                )
                if reason == "Repeated greeting detected.":
                    llm_text = (
                        "Let's continue from where we left off. "
                        "What would you like to talk about next?"
                    )
                elif reason == "Repeated empathy detected.":
                    llm_text = (
                        "I want to better understand what you're experiencing. "
                        "Could you tell me a little more about what's been happening?"
                    )
                elif reason == "Repeated introduction detected.":
                    llm_text = (
                        "Let's continue our conversation. "
                        "What would you like to share or ask next?"
                    )
                elif reason == "Repeated closing detected.":
                    llm_text = (
                        "Before we end our conversation, "
                        "is there anything else you'd like to talk about?"
                    )
                elif reason == "The response is too short.":
                    llm_text = (
                        "I'd like to give you a more helpful response. "
                        "Could you tell me a little more about your situation?"
                    )
                elif reason == "The response is empty.":
                    llm_text = (
                        "I want to make sure I understand you correctly. "
                        "Could you tell me a little more about what's on your mind?"
                    )
                else:
                    llm_text = (
                        "I don't want to make assumptions about what you're going through. "
                        "Could you share a little more so I can respond more appropriately?"
                    )
            
            # -----------------------------------------
            # Final Response
            # -----------------------------------------
            
            return ChatResponse(

                success=True,

                response=llm_text,

                emotion=emotion.emotion,

                sentiment=emotion.sentiment,

                language=language.language,
                topic=conversation_topic.value,
                state=conversation_state.value,
                escalated=(
                    safety.should_escalate
                    or emotion.is_negative
                ),

                confidence=emotion.confidence,
            )

        except Exception:
            logger.exception(
                "AIService failed while processing message: %r",
                message,
            )

            return ChatResponse(
                success=False,
                response=(
                    "An unexpected error occurred while "
                    "processing your request."
                ),
                emotion="Unknown",
                sentiment="Unknown",
                language="Unknown",
                topic="Unknown",
                state="Unknown",
                escalated=False,
                confidence=0.0,
            )
        
        finally:
            print_pipeline_metrics()
        