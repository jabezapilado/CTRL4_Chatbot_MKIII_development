"""
AI Service

Main AI orchestration service for CTRL4 Chatbot MK III.

Responsibilities

- Safety Validation
- Language Detection
- Emotion Detection
- Knowledge Retrieval (RAG)
- Prompt Construction
- LLM Response Generation

CTRL4 Chatbot MK III

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from __future__ import annotations
import logging
import re
import time
from typing import Final

from dataclasses import dataclass

from .emotion_service import EmotionService
from .language_service import LanguageService
from .rag_service import RAGService
from .prompt_builder import PromptBuilder, PromptInput
from .llm_service import LLMService
from .safety_service import SafetyService
from .intent_service import IntentService
from .topic_service import TopicService
from .metadata_service import MetadataExtractionService
from .conversation_state import ConversationState
from .conversation_topic import ConversationTopic
from .response_validator import ResponseValidator
from .response_safety_service import ResponseSafetyService
from .conversation_history import normalize_conversation_history
from .operational_guidance_service import OperationalGuidanceService
from .settings_service import SettingsService

logger = logging.getLogger(__name__)

_COURSE_CODE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(?:[A-Z]{5,}|[A-Z]{2,}[ -]?\d{2,4})\b"
)



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

    intent: str

    normalized_emotion: str | None

    normalized_topic: str | None

    metadata: dict[str, str | None] | None


class AIService:

    def __init__(
        self,
        safety: SafetyService | None = None,
        language: LanguageService | None = None,
        emotion: EmotionService | None = None,
        rag: RAGService | None = None,
        prompt_builder: PromptBuilder | None = None,
        llm: LLMService | None = None,
        intent: IntentService | None = None,
        topic_classifier: TopicService | None = None,
        metadata_extractor: MetadataExtractionService | None = None,
        response_safety: ResponseSafetyService | None = None,
        operational_guidance: OperationalGuidanceService | None = None,
        faq_settings: SettingsService | None = None,
    ):

        self.safety = safety or SafetyService()

        self.language = language or LanguageService()

        self.emotion = emotion or EmotionService()

        self.rag = rag or RAGService()

        self.prompt_builder = prompt_builder or PromptBuilder()

        self.llm = llm or LLMService()

        self.intent = intent or IntentService()

        self.topic_classifier = topic_classifier or TopicService()

        self.metadata_extractor = (
            metadata_extractor or MetadataExtractionService()
        )
        
        self.response_validator = ResponseValidator()

        self.response_safety = response_safety or ResponseSafetyService()

        self.operational_guidance = operational_guidance or OperationalGuidanceService()
        self.faq_settings = faq_settings or SettingsService()
    
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
            "it's just",
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

        raw_message = message
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

        if _COURSE_CODE_PATTERN.search(raw_message):
            return ConversationTopic.ACADEMICS

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
        user: dict | None = None,
    ) -> ChatResponse:

        if conversation is None:
            conversation = []
        conversation = normalize_conversation_history(conversation)
        
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
            # Language Detection
            # -----------------------------------------

            language_start = time.perf_counter()
            language = self.language.detect(message)
            language_time = time.perf_counter() - language_start

            # -----------------------------------------
            # Safety Validation
            # -----------------------------------------

            safety_start = time.perf_counter()
            safety = self.safety.check(
                message,
                language=language.language,
            )
            safety_time = time.perf_counter() - safety_start

            intent = self.intent.detect(message)
            normalized_topic = self.topic_classifier.classify(message)
            metadata = self.metadata_extractor.extract(message)

            if safety.response:

                return ChatResponse(
                    success=True,
                    response=safety.response,
                    emotion="Unknown",
                    sentiment="Unknown",
                    language=language.language,
                    topic="Unknown",
                    state="Unknown",
                    escalated=safety.should_escalate,
                    confidence=0.0,
                    intent=intent,
                    normalized_emotion=(
                        "crisis" if safety.should_escalate else None
                    ),
                    normalized_topic=normalized_topic,
                    metadata=metadata.to_dict(),
                )

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
                "Conversation classified | state=%s topic=%s",
                conversation_state.value,
                conversation_topic.value,
            )

            # Live operational answers are source-owned configuration, not RAG
            # context or provider prior knowledge. Safety remains active before
            # the deterministic response is returned.
            operational_answer = self.operational_guidance.answer(message, user)
            if operational_answer is not None:
                response_safety = self.response_safety.validate(
                    operational_answer.response,
                    [operational_answer],
                )
                response = (
                    response_safety.replacement
                    if not response_safety.allowed and response_safety.replacement
                    else operational_answer.response
                )
                return ChatResponse(
                    success=True,
                    response=response,
                    emotion=emotion.emotion,
                    sentiment=emotion.sentiment,
                    language=language.language,
                    topic=conversation_topic.value,
                    state=conversation_state.value,
                    escalated=(
                        safety.should_escalate
                        or emotion.normalized_emotion in {"crisis", "distressed"}
                    ),
                    confidence=emotion.confidence,
                    intent=intent,
                    normalized_emotion=emotion.normalized_emotion,
                    normalized_topic=normalized_topic,
                    metadata=metadata.to_dict(),
                )

            faq_answer = self.faq_settings.answer_faq(message, user)
            if faq_answer is not None:
                response_safety = self.response_safety.validate(
                    faq_answer.response,
                    [faq_answer],
                )
                response = (
                    response_safety.replacement
                    if not response_safety.allowed and response_safety.replacement
                    else faq_answer.response
                )
                return ChatResponse(
                    success=True,
                    response=response,
                    emotion=emotion.emotion,
                    sentiment=emotion.sentiment,
                    language=language.language,
                    topic=conversation_topic.value,
                    state=conversation_state.value,
                    escalated=(
                        safety.should_escalate
                        or emotion.normalized_emotion in {"crisis", "distressed"}
                    ),
                    confidence=emotion.confidence,
                    intent=intent,
                    normalized_emotion=emotion.normalized_emotion,
                    normalized_topic=normalized_topic,
                    metadata=metadata.to_dict(),
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

                    intent=intent,

                    normalized_emotion=emotion.normalized_emotion,

                    normalized_topic=normalized_topic,

                    metadata=metadata.to_dict(),

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
                if reason == "The response is too short.":
                    llm_text = (
                        "I'd like to give you a more helpful response. "
                        "Could you tell me a little more about your situation?"
                    )
                elif reason == "The response is empty.":
                    llm_text = (
                        "I want to make sure I understand you correctly. "
                        "Could you tell me a little more about what's on your mind?"
                    )
                elif reason == "Repeated response detected.":
                    llm_text = (
                        "I want to avoid repeating the same response. "
                        "Please tell me which part would be most helpful to explore."
                    )
                else:
                    llm_text = (
                        "I don't want to make assumptions about what you're going through. "
                        "Could you share a little more so I can respond more appropriately?"
                    )

            response_safety = self.response_safety.validate(
                llm_text,
                documents,
            )
            if not response_safety.allowed:
                logger.warning(
                    "Generated response replaced by safety validation (category=%s).",
                    response_safety.category,
                )
                llm_text = response_safety.replacement or llm_text
            
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
                    or emotion.normalized_emotion in {"crisis", "distressed"}
                ),

                confidence=emotion.confidence,
                intent=intent,
                normalized_emotion=emotion.normalized_emotion,
                normalized_topic=normalized_topic,
                metadata=metadata.to_dict(),
            )

        except Exception as exc:
            logger.error(
                "AIService chat processing failed (exception_type=%s).",
                type(exc).__name__,
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
                intent="unknown",
                normalized_emotion=None,
                normalized_topic=None,
                metadata=None,
            )
        
        finally:
            print_pipeline_metrics()
