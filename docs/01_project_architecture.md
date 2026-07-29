# CTRL4 Chatbot MK II
## 01 — Project Architecture

**Version:** MK II Stable (v2.0.0)

**Authors**

- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell

**Capstone Project**

Development of an AI-Powered Guidance Chatbot for Inquiry Management Using NLP-Based Negative Emotion Detection

**Institution**

Holy Angel University

**Program**

Bachelor of Science in Computer Science

**Academic Year**

2026–2027

**Last Updated**

July 2026

---

# Overview

CTRL4 Chatbot MK II is an AI-powered web-based guidance chatbot developed for the Holy Angel University School of Computing. The system was designed to provide students with immediate access to guidance-related information while supporting emotionally aware conversations through artificial intelligence.

Unlike conventional rule-based chatbots, CTRL4 Chatbot MK II adopts a modular service-oriented architecture. Every student message passes through multiple artificial intelligence services before a response is generated. These services perform safety validation, language detection, emotion detection, knowledge retrieval, prompt construction, and large language model (LLM) generation.

The chatbot combines traditional Natural Language Processing (NLP), Retrieval-Augmented Generation (RAG), and modern Large Language Models (LLMs) to generate responses that are accurate, context-aware, empathetic, and grounded in verified Guidance Office information.

By separating artificial intelligence into independent modules, the system becomes easier to maintain, evaluate, extend, and improve without affecting the rest of the application.

---

# Project Objectives

The architecture of CTRL4 Chatbot MK II was designed to achieve the following objectives:

- Provide students with reliable AI-assisted guidance support.
- Detect the emotional context expressed in student messages.
- Generate supportive, empathetic, and context-aware responses.
- Retrieve verified Guidance Office information through Retrieval-Augmented Generation (RAG).
- Detect crisis-related conversations and prioritize student safety.
- Maintain a modular architecture that supports future enhancements and additional language model providers.

---

# System Architecture

The chatbot follows a layered architecture that separates presentation, business logic, artificial intelligence services, and language model providers.

```text
                           Student
                               │
                               ▼
             Frontend (HTML, CSS, JavaScript)
                               │
                               ▼
                 Flask Backend Application
                               │
                               ▼
                          AIService
                               │
      ┌────────────────────────┼────────────────────────┐
      │                        │                        │
      ▼                        ▼                        ▼
SafetyService          LanguageService         EmotionService
                               │
                               ▼
                          RAGService
                               │
                               ▼
                        PromptBuilder
                               │
                               ▼
                          LLMService
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
         GeminiProvider              OllamaProvider
                               │
                               ▼
                     Generated AI Response
                               │
                               ▼
                            Student
```

Each layer has a single responsibility, improving maintainability, readability, and scalability.

---

# AI Processing Pipeline

Every student message follows the same processing pipeline before a response is returned.

```text
Student Message
        │
        ▼
Safety Validation
        │
        ▼
Language Detection
        │
        ▼
Emotion Detection
        │
        ▼
Knowledge Retrieval (RAG)
        │
        ▼
Prompt Construction
        │
        ▼
Large Language Model
(Gemini or Ollama)
        │
        ▼
Generated Response
```

This sequential workflow allows the chatbot to understand the student's message, retrieve verified institutional information, and generate supportive responses while maintaining safety and factual accuracy.

---

# Why This Architecture?

CTRL4 Chatbot MK II adopts a modular service-oriented architecture instead of placing all artificial intelligence logic inside a single component.

This design offers several advantages:

- Improved maintainability by separating each responsibility into its own service.
- Easier debugging because individual services can be tested independently.
- Better scalability by allowing new AI modules to be integrated without redesigning the entire application.
- Flexible language model integration through interchangeable providers.
- Reduced coupling between artificial intelligence components and application logic.

Each module communicates through clearly defined interfaces, making the architecture easier to understand and extend for future development.

---

# Artificial Intelligence Workflow

The following sequence illustrates how the chatbot processes a student's message.

1. The student submits a message through the web interface.
2. The backend receives the request.
3. SafetyService evaluates whether the message contains crisis-related language.
4. LanguageService determines whether the message is written in English, Filipino, or Taglish.
5. EmotionService predicts the emotional context of the message.
6. RAGService retrieves relevant Guidance Office information from the knowledge base.
7. PromptBuilder combines all contextual information into a single prompt.
8. LLMService forwards the prompt to the configured language model provider.
9. GeminiProvider or OllamaProvider generates the response.
10. The final response is returned to the student.

This pipeline ensures that every response considers emotional context, verified institutional information, and conversation history before generation.

---

# Core Components

CTRL4 Chatbot MK II is composed of several independent services that work together to generate safe, accurate, and context-aware responses.

Each service is responsible for a single task, following the principle of separation of concerns.

---

## AIService

`AIService` is the central orchestrator of the chatbot. It coordinates the entire artificial intelligence pipeline by executing each service in sequence and returning the final chatbot response.

Its responsibilities include:

- Managing the AI processing workflow
- Coordinating all AI services
- Handling exceptions
- Returning standardized chatbot responses
- Recording pipeline performance

The AIService acts as the entry point of the chatbot's intelligence.

---

## SafetyService

SafetyService performs the first stage of the pipeline.

Before any AI processing begins, it analyzes the student's message for crisis-related content that may require immediate attention.

Current responsibilities include:

- Suicide detection
- Self-harm detection
- Crisis language detection
- Immediate safety response generation
- Escalation flagging

Student safety always has the highest priority. When a crisis is detected, the chatbot bypasses normal AI generation and returns a predefined safety response encouraging the student to seek immediate professional support.

---

## LanguageService

LanguageService detects the language used in the student's message.

Supported languages include:

- English
- Filipino
- Taglish (mixed English and Filipino)

The detected language is passed to PromptBuilder so that the chatbot can naturally mirror the student's preferred language throughout the conversation.

---

## EmotionService

EmotionService predicts the emotional context of the student's message using a transformer-based emotion classification model.

The current model recognizes the following emotional categories:

- Positive
- Neutral
- Sadness
- Fear
- Anger

For every prediction, the service also returns:

- Primary emotion
- Overall sentiment
- Confidence score

Emotion predictions are used only as supporting information during prompt construction. The chatbot always prioritizes the student's actual message and conversation context over model predictions.

---

## RAGService

The Retrieval-Augmented Generation (RAG) service retrieves relevant institutional information from the Guidance Office Knowledge Base.

Instead of relying solely on the language model's internal knowledge, the chatbot searches its indexed knowledge base for verified information before generating a response.

The knowledge base contains information such as:

- Office hours
- Counseling services
- Appointment procedures
- Guidance Office policies
- Frequently Asked Questions
- Referral information

This approach significantly reduces hallucinations while improving factual accuracy.

---

## PromptBuilder

PromptBuilder constructs the final prompt that is submitted to the selected language model.

The prompt combines multiple sources of information, including:

- Student message
- Conversation history
- Detected language
- Predicted emotion
- Retrieved Guidance Office information
- Safety instructions
- Conversation guidelines
- Personality guidelines

The resulting prompt provides the language model with sufficient context to generate accurate, empathetic, and institutionally appropriate responses.

---

## LLMService

LLMService acts as the communication layer between the chatbot and supported language model providers.

Its responsibilities include:

- Selecting the configured provider
- Sending prompts
- Receiving generated responses
- Standardizing provider outputs
- Handling provider errors

Because of this abstraction layer, the chatbot's business logic remains independent of the underlying language model.

---

# LLM Provider Architecture

CTRL4 Chatbot MK II implements a provider abstraction layer that allows multiple language model providers to be used interchangeably.

Every provider implements a common interface through the `BaseProvider` class.

Current providers include:

- GeminiProvider
- OllamaProvider

Future providers may include:

- OpenAI
- Claude
- Groq
- DeepSeek
- Mistral

Since all providers follow the same interface, switching between providers requires only a configuration change instead of modifying the application code.

---

# Project Structure

The project is organized into four major components.

```text
CTRL4_Chatbot/

├── backend/
│   ├── server/
│   │   ├── services/
│   │   ├── llm_providers/
│   │   ├── routes.py
│   │   ├── config.py
│   │   └── ...
│   │
│   ├── scripts/
│   ├── sql/
│   └── app.py
│
├── frontend/
│   ├── static/
│   ├── templates/
│   └── ...
│
├── ai_engine/
│   ├── configs/
│   ├── core/
│   ├── knowledge_base/
│   ├── data/
│   └── models/
│
└── docs/
```

The project structure separates presentation, backend services, artificial intelligence components, datasets, and documentation into independent directories.

This organization simplifies development, improves readability, and supports future scalability.

---

# Interaction Between Components

The following diagram illustrates how the primary components interact during a conversation.

```text
Student
    │
    ▼
Frontend
    │
    ▼
Flask Backend
    │
    ▼
AIService
    │
    ├── SafetyService
    ├── LanguageService
    ├── EmotionService
    ├── RAGService
    ├── PromptBuilder
    └── LLMService
            │
            ▼
GeminiProvider / OllamaProvider
            │
            ▼
Generated Response
            │
            ▼
Frontend
            │
            ▼
Student
```

Each component communicates through clearly defined interfaces, ensuring that responsibilities remain independent while contributing to a unified response generation pipeline.

---

# Design Principles

CTRL4 Chatbot MK II follows modern software engineering principles to improve maintainability, scalability, and long-term development.

## Modular Design

Every major responsibility is implemented as an independent service.

Examples include:

- AIService
- SafetyService
- LanguageService
- EmotionService
- RAGService
- PromptBuilder
- LLMService

This modular approach allows each component to be developed, tested, and maintained independently.

---

## Separation of Concerns

The project separates presentation, backend logic, artificial intelligence, and documentation into independent modules.

| Layer                  | Responsibility                               |
| ---------------------- | -------------------------------------------- |
| Frontend               | User interface and interaction               |
| Backend                | Business logic and API endpoints             |
| AI Engine              | Models, datasets, and knowledge retrieval    |
| Documentation          | Technical and project documentation          |

This organization reduces coupling between components and simplifies future maintenance.

---

## Scalability

The architecture was designed to accommodate future enhancements without major structural changes.

Examples include:

- Additional language model providers
- Intent classification
- Conversation memory
- Emotional trend analysis
- Counselor analytics
- Mobile application support

---

## Maintainability

Reusable services, centralized configuration files, and standardized interfaces reduce code duplication and simplify future updates.

Each service has a clearly defined responsibility, making debugging and testing more efficient.

---

## Provider Independence

Language model providers are abstracted behind a common interface.

This allows the chatbot to switch between supported providers without changing application logic.

Current providers include:

- GeminiProvider
- OllamaProvider

Future providers can be added by implementing the `BaseProvider` interface.

---

## Safety First

Student safety is the highest priority of the chatbot.

Messages indicating:

- Suicide
- Self-harm
- Immediate danger
- Crisis situations

are detected before response generation begins. When necessary, the chatbot immediately returns an appropriate safety response and recommends seeking professional assistance.

---

# Technology Stack

| Component                 | Technology                      |
| ------------------------- | ------------------------------- |
| Programming Language      | Python 3                        |
| Backend Framework         | Flask                           |
| Frontend                  | HTML5, CSS3, JavaScript         |
| Database                  | MySQL                           |
| Emotion Detection         | DistilBERT                      |
| Language Detection        | langdetect                      |
| Knowledge Retrieval       | FAISS + Sentence Transformers   |
| Large Language Models     | Google Gemini, Ollama           |
| Environment Configuration | python-dotenv                   |
| Version Control           | Git & GitHub                    |

---

# Current Development Status

CTRL4 Chatbot MK II has reached a stable implementation phase.

| Component                         | Status        |
| --------------------------------- | ------------- |
| Authentication                    | ✅ Complete   |
| Student Chatbot                   | ✅ Complete   |
| Appointment Management            | ✅ Complete   |
| Staff Dashboard                   | ✅ Complete   |
| Chat Takeover                     | ✅ Complete   |
| Emotion Detection                 | ✅ Complete   |
| Language Detection                | ✅ Complete   |
| Safety Validation                 | ✅ Complete   |
| Retrieval-Augmented Generation    | ✅ Complete   |
| Prompt Builder                    | ✅ Complete   |
| LLM Service                       | ✅ Complete   |
| Gemini Provider                   | ✅ Complete   |
| Ollama Provider                   | ✅ Complete   |
| Performance Monitoring            | ✅ Complete   |
| Knowledge Base Integration        | ✅ Complete   |

---

# Future Enhancements (MK III)

Future versions of CTRL4 Chatbot may include additional artificial intelligence capabilities and platform improvements.

Planned enhancements include:

- Long-term conversation memory
- Intent classification
- Emotional trend analytics
- Counselor conversation summaries
- Real-time streaming responses
- Mobile application support
- Google Gen AI SDK migration
- Additional language model providers
- Improved multilingual support
- Advanced appointment scheduling
- Student conversation analytics

These enhancements aim to improve personalization, scalability, and decision support while maintaining the chatbot's role as an AI-assisted guidance companion.

---

# Conclusion

CTRL4 Chatbot MK II implements a modular, service-oriented artificial intelligence architecture that integrates emotion detection, language detection, Retrieval-Augmented Generation (RAG), prompt engineering, and modern large language models to provide reliable guidance support for students.

Rather than relying solely on generative AI, the chatbot combines multiple specialized services that work together to produce responses that are context-aware, emotionally supportive, and grounded in verified Guidance Office information.

The provider abstraction layer allows multiple language models to be used interchangeably, while the modular architecture ensures that future improvements can be integrated with minimal impact on the existing system.

This architecture provides a strong foundation for future development while supporting the project's primary objective of delivering accessible, accurate, and student-centered guidance services through artificial intelligence.

---

# References

The architecture of CTRL4 Chatbot MK II is based on established software engineering principles and modern artificial intelligence techniques, including:

- Modular Software Architecture
- Service-Oriented Design
- Retrieval-Augmented Generation (RAG)
- Transformer-based Natural Language Processing
- Prompt Engineering
- Large Language Model Provider Abstraction

These concepts guided the design decisions implemented throughout the system.