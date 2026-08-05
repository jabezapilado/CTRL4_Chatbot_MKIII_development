# CTRL4 Chatbot Bible

Version: MK II Stable (v2.0.0)

---

# Purpose

The CTRL4 Chatbot Bible serves as the primary technical reference for the project.

It documents the architecture, design principles, coding standards, and development philosophy of CTRL4 Chatbot MK II.

This document should be updated whenever major architectural or design changes are introduced.

---

# Vision

CTRL4 Chatbot aims to provide students of the Holy Angel University School of Computing with a safe, reliable, and intelligent AI Guidance Assistant that supports the Guidance Office without replacing licensed guidance counselors.

The chatbot is designed to:

- Provide 24/7 student assistance.
- Deliver accurate Guidance Office information.
- Support multilingual conversations.
- Detect emotional context.
- Encourage professional support when appropriate.
- Maintain student safety as the highest priority.

---

# Design Principles

## Modular

Every major responsibility belongs to its own service.

Examples:

- EmotionService
- LanguageService
- SafetyService
- RAGService
- PromptBuilder
- LLMService

---

## Separation of Concerns

Each module performs one responsibility only.

Frontend

- User Interface

Backend

- Business Logic

AI

- Intelligence

Database

- Storage

---

## Provider Abstraction

The chatbot should never depend on a single LLM.

Instead, providers implement the same interface.

Current providers:

- GeminiProvider
- OllamaProvider

Future providers may include:

- OpenAI
- Claude
- Groq
- DeepSeek
- Mistral

---

## AI First

Business logic should remain independent from the selected language model.

Changing the LLM should never require changes to AIService.

---

# AI Pipeline

Student Message

↓

Safety Validation

↓

Language Detection

↓

Emotion Detection

↓

Knowledge Retrieval (RAG)

↓

Prompt Construction

↓

LLM Generation

↓

Response

---

# Folder Structure

CTRL4_Chatbot/

```
backend/
frontend/
ai_engine/
docs/
```

---

Backend

```
server/

services/

llm_providers/

routes.py

config.py
```

---

AI Engine

```
knowledge_base/

core/

configs/
```

---

# Core Components

## AIService

Central orchestrator.

Responsibilities:

- Coordinate the AI pipeline.
- Call all supporting services.
- Return the final response.

---

## SafetyService

Responsible for:

- Suicide detection
- Self-harm detection
- Crisis escalation
- Unsafe content detection

---

## LanguageService

Detects:

- English
- Filipino
- Taglish

Used for prompt adaptation.

---

## EmotionService

Predicts:

- Emotion
- Sentiment
- Confidence

Used only as supporting context.

Student messages always have higher priority.

---

## RAGService

Retrieves official Guidance Office information.

Used for:

- Office hours
- Policies
- Appointments
- Services
- Referrals

Never invent official information.

---

## PromptBuilder

Constructs the final prompt sent to the LLM.

Includes:

- Conversation history
- Retrieved documents
- Emotion
- Language
- Student message
- Safety instructions

---

## LLMService

Responsible for:

- Selecting providers
- Sending prompts
- Returning responses

Does not perform business logic.

---

# Providers

Every provider implements BaseProvider.

Current:

- GeminiProvider
- OllamaProvider

Future:

- OpenAIProvider
- ClaudeProvider
- GroqProvider
- DeepSeekProvider

---

# Prompt Engineering Philosophy

Prompts should:

- Be supportive
- Avoid diagnoses
- Encourage reflection
- Use official Guidance information only
- Never invent policies
- Mirror the student's language
- Respect emotional context

---

# Coding Standards

Naming

Classes

PascalCase

Functions

snake_case

Variables

snake_case

Constants

UPPER_CASE

---

Comments

Write comments that explain "why", not "what".

Avoid obsolete comments.

Remove development placeholders before release.

---

Logging

Log:

- Initialization
- AI pipeline timing
- Exceptions

Never log:

- Passwords
- API keys
- Student personal information

---

# Error Handling

Every AI provider must:

- Return structured responses.
- Never crash AIService.
- Report meaningful errors.
- Allow fallback providers in future versions.

---

# Performance

Current pipeline:

Safety

↓

Language

↓

Emotion

↓

RAG

↓

Prompt

↓

LLM

Pipeline timing is measured for debugging and optimization.

---

# Security

Secrets must remain inside:

.env

Never commit:

- API Keys
- Database passwords
- Tokens

---

# Version History

MK I

Prototype chatbot

↓

MK II

Modular AI architecture

↓

MK III (Planned)

Conversation memory

Analytics

Counselor summaries

Streaming responses

Better personalization

---

# Future Roadmap

Planned improvements:

- Google Gen AI SDK migration
- Long-term conversation memory
- Intent classification
- Emotional trend analysis
- Real-time streaming
- WebSocket support
- Dashboard analytics
- Better appointment scheduling

---

# Authors

Apilado, Jabez Timothy E.

Quilantang, Grant Mihkael D.

Lanix, Iligan

Wylengco, Teyshaun Zell