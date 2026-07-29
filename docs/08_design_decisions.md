# CTRL4 Chatbot MK II
## 08 — Design Decisions

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

Developing CTRL4 Chatbot MK II required numerous architectural and implementation decisions involving machine learning, Retrieval-Augmented Generation (RAG), large language models (LLMs), and web application development.

Every major decision was made after evaluating system requirements, deployment constraints, maintainability, scalability, and long-term extensibility.

This document explains the rationale behind the most significant design decisions implemented throughout the project.

---

# Objectives

This document aims to:

- Explain the reasoning behind major architectural decisions.
- Document implementation trade-offs.
- Improve long-term maintainability.
- Support future development.
- Provide technical justification for the selected technologies.

---

# Design Decision 1
## Why Use a Hybrid AI Architecture?

Instead of relying entirely on a Large Language Model, CTRL4 Chatbot combines multiple artificial intelligence components.

The implemented architecture includes:

- Safety Validation
- Language Detection
- Emotion Detection
- Retrieval-Augmented Generation (RAG)
- Prompt Engineering
- Large Language Model

### Rationale

Each component performs a specialized task.

Benefits include:

- Better factual accuracy.
- Reduced hallucinations.
- Emotion-aware responses.
- Modular implementation.
- Easier maintenance.

---

# Design Decision 2
## Why Use a Separate Emotion Detection Model?

Although modern LLMs can infer emotions, the project implements a dedicated emotion classifier.

### Rationale

- Faster inference.
- Consistent emotion prediction.
- Lower computational cost.
- Standardized emotion categories.
- Easier evaluation and benchmarking.

The emotion prediction serves as contextual information during prompt construction rather than replacing the language model.

---

# Design Decision 3
## Why Choose DistilBERT?

Several transformer architectures were evaluated.

### Selected Model

- DistilBERT

### Alternatives Considered

- BERT
- RoBERTa
- DeBERTa

### Rationale

- Smaller model size.
- Faster inference.
- Lower memory usage.
- Excellent NLP performance.
- Seamless Hugging Face integration.

DistilBERT provides an excellent balance between efficiency and classification accuracy for real-time deployment.

---

# Design Decision 4
## Why Merge Multiple Emotion Datasets?

No publicly available dataset completely represents the emotional expressions expected within university guidance conversations.

The project therefore combines several datasets.

Integrated datasets include:

- GoEmotions
- ISEAR
- DAIR-AI Emotion

### Benefits

- Increased dataset size.
- Improved linguistic diversity.
- Better model generalization.
- Reduced dataset bias.
- Broader emotional coverage.

---

# Design Decision 5
## Why Standardize Emotion Labels?

Each source dataset uses its own emotion taxonomy.

Rather than training multiple independent classifiers, all labels are mapped into a unified emotion taxonomy.

### Standardized Categories

- Positive
- Neutral
- Anger
- Sadness
- Fear

This simplifies training while improving compatibility across datasets.

---

# Design Decision 6
## Why Use Retrieval-Augmented Generation?

Official Guidance Office information changes over time.

Instead of embedding institutional information directly into the language model, CTRL4 retrieves relevant documents during every conversation.

### Benefits

- Institution-approved responses.
- Reduced hallucinations.
- Easier knowledge updates.
- Better factual consistency.
- Improved response reliability.

This allows the chatbot to remain accurate without retraining machine learning models whenever institutional information changes.

---

# Design Decision 7
## Why Separate the Knowledge Base from the AI Model?

Institutional documents are stored independently from the emotion model.

### Rationale

The emotion classifier learns emotional patterns.

The knowledge base stores factual institutional information.

Separating these responsibilities:

- Simplifies maintenance.
- Improves modularity.
- Enables independent updates.
- Supports Retrieval-Augmented Generation.

---

# Design Decision 8
## Why Support Multiple LLM Providers?

The chatbot supports both cloud-based and local language models.

Current providers include:

- Google Gemini
- Ollama

### Benefits

- Flexible deployment.
- Offline development.
- Reduced vendor dependency.
- Easier experimentation.
- Future scalability.

The provider abstraction layer allows additional models to be integrated without modifying the application's business logic.

---

# Design Decision 9
## Why Implement a Provider Abstraction Layer?

Rather than communicating directly with Gemini or Ollama, all requests pass through `LLMService`.

### Advantages

- Unified interface.
- Cleaner code.
- Easier maintenance.
- Provider independence.
- Simplified future integrations.

This design follows the Dependency Inversion Principle by separating business logic from provider-specific implementations.

---

# Design Decision 10
## Why Use a Modular Service Architecture?

Artificial intelligence functionality is divided into independent services.

Current services include:

- AIService
- SafetyService
- LanguageService
- EmotionService
- RAGService
- PromptBuilder
- LLMService

### Benefits

- Easier debugging.
- Independent testing.
- Better scalability.
- Improved maintainability.
- Reduced coupling.

Each service focuses on a single responsibility, improving code quality and readability.

---

# Design Decision 11
## Why Use Configuration Files?

Model settings, provider selection, and environment-specific values are stored outside the application code.

Examples include:

- Environment variables
- JSON configuration files
- Model settings

### Advantages

- Easier experimentation.
- Cleaner implementation.
- Improved reproducibility.
- Simpler deployment.

---

# Design Decision 12
## Why Implement Performance Monitoring?

Each stage of the AI pipeline records its execution time.

Current measurements include:

- Safety validation
- Language detection
- Emotion detection
- Knowledge retrieval
- Prompt construction
- LLM generation

### Benefits

- Performance optimization.
- Easier debugging.
- Bottleneck identification.
- System evaluation.

This information is valuable during development and future optimization.

---

# Design Decision 13
## Why Prioritize Student Safety?

Student well-being is the primary objective of the chatbot.

Safety validation occurs before any AI response generation.

Potential crisis situations include:

- Suicide ideation
- Self-harm
- Immediate danger

When detected, the chatbot bypasses normal response generation and returns an appropriate safety response encouraging professional support.

---

# Future Design Considerations

Future architectural enhancements may include:

- Intent classification.
- Conversation-level emotion tracking.
- Risk prediction models.
- Automated knowledge base updates.
- Multilingual emotion recognition.
- Long-term conversation memory.
- Streaming LLM responses.
- Counselor analytics dashboard.
- Additional LLM providers.

These improvements can be integrated without major architectural redesign due to the modular nature of the current implementation.

---

# Summary

The architectural decisions implemented in CTRL4 Chatbot MK II emphasize modularity, scalability, maintainability, and responsible AI design.

Rather than relying on a single artificial intelligence model, the system combines specialized machine learning components, Retrieval-Augmented Generation, prompt engineering, and provider-independent large language model integration to deliver emotionally aware and institutionally accurate guidance support.

These design decisions establish a flexible foundation for future research, system enhancements, and real-world deployment while maintaining the project's focus on supporting students through accessible, reliable, and ethical AI-assisted guidance services.