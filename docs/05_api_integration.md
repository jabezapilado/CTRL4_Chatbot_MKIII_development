# CTRL4 Chatbot MK II
## 05 — API Integration & External Services

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

CTRL4 Chatbot MK II integrates multiple external services to provide intelligent, context-aware, and reliable responses.

Rather than depending entirely on internally developed machine learning models, the chatbot combines local artificial intelligence components with cloud-based language models and semantic retrieval technologies.

This hybrid integration enables the system to balance response quality, factual accuracy, and deployment flexibility.

---

# Objectives

The API integration layer was designed to achieve the following objectives:

- Connect the chatbot to modern large language models.
- Allow multiple LLM providers through a unified interface.
- Separate external APIs from application logic.
- Improve maintainability through provider abstraction.
- Support future provider expansion without modifying the chatbot architecture.

---

# Integration Architecture

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
    ▼
LLMService
    │
    ├──────────────┐
    ▼              ▼
GeminiProvider  OllamaProvider
    │              │
    ▼              ▼
Large Language Models
    │
    ▼
Generated Response
```

The backend communicates only with `LLMService`.

`LLMService` delegates response generation to the configured provider, making the rest of the application independent of the underlying language model.

---

# Supported Providers

CTRL4 Chatbot MK II currently supports multiple language model providers.

| Provider           | Type               | Status        |
| ------------------ | ------------------ | ------------- |
| Google Gemini      | Cloud API          | ✅ Supported  |
| Ollama             | Local Inference    | ✅ Supported  |

The active provider can be changed through the application's configuration without modifying business logic.

---

# Gemini Integration

Google Gemini serves as the primary cloud-based language model provider.

Its responsibilities include:

- Natural language understanding
- Context-aware response generation
- Emotional conversational responses
- Guidance conversation assistance

Gemini receives a fully constructed prompt from the PromptBuilder, which includes:

- Student message
- Conversation history
- Emotion prediction
- Language detection
- Retrieved Guidance Office information
- System instructions
- Personality guidelines

---

# Ollama Integration

Ollama provides a local inference alternative for development and offline testing.

Advantages include:

- No internet dependency
- Local execution
- Easy experimentation with open-source models
- Lower operational cost during development

Although local models may produce lower-quality responses than cloud models, they provide flexibility for testing and research.

---

# Provider Abstraction

All language model providers implement the same interface through the `BaseProvider` class.

```text
BaseProvider
      │
      ├──────────────┐
      ▼              ▼
GeminiProvider  OllamaProvider
```

This abstraction ensures that each provider exposes the same functionality while handling provider-specific implementation details internally.

---

# LLM Request Flow

Every chatbot response follows the same sequence.

```text
PromptBuilder
        │
        ▼
LLMService
        │
        ▼
Selected Provider
        │
        ▼
Large Language Model
        │
        ▼
Generated Response
```

The application never communicates directly with individual providers.

Instead, all communication passes through `LLMService`.

---

# Prompt Transmission

Before sending a request to the selected language model, the PromptBuilder constructs a complete prompt containing:

- System instructions
- Student message
- Conversation history
- Emotion prediction
- Language detection
- Retrieved Guidance Office knowledge
- Personality guidelines
- Safety guidelines

Providing structured context improves response quality while maintaining consistent chatbot behavior.

---

# Error Handling

The API integration layer includes standardized error handling to improve reliability.

Common scenarios include:

- Network failures
- Authentication errors
- Rate limit exceeded
- Provider unavailable
- Invalid responses

When an error occurs, the chatbot returns a user-friendly fallback message instead of exposing internal implementation details.

---

# Configuration

Provider configuration is managed separately from the application logic.

Typical configuration values include:

| Setting              | Description                         |
| -------------------- | ----------------------------------- |
| Active Provider      | Selected LLM provider               |
| API Key              | Authentication credential           |
| Model Name           | Selected language model             |
| Temperature          | Response creativity                 |
| Maximum Tokens       | Response length limit               |

Environment variables are used to protect sensitive credentials.

---

# Performance Monitoring

The AI pipeline records the execution time of each processing stage.

Current measurements include:

- Safety validation
- Language detection
- Emotion detection
- RAG retrieval
- Prompt construction
- LLM generation
- Total pipeline time

These metrics assist with debugging, optimization, and system evaluation.

---

# Security Considerations

Several security measures are implemented during API integration.

- API keys are stored in environment variables.
- Sensitive credentials are excluded from version control.
- Providers are accessed through a centralized service layer.
- User messages are processed only during active requests.
- Internal errors are not exposed to end users.

---

# Future Improvements

Future API enhancements include:

- Google Gen AI SDK migration
- Streaming response generation
- Automatic provider fallback
- Load balancing between providers
- Additional LLM providers
- Response caching
- Retry mechanisms
- Usage analytics

---

# Summary

The API integration layer enables CTRL4 Chatbot MK II to communicate with multiple large language model providers through a unified and extensible architecture.

By separating provider-specific logic from the application's business logic, the chatbot remains modular, maintainable, and adaptable to future AI technologies while providing reliable and context-aware guidance responses.