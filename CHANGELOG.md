# Changelog

All notable changes to the CTRL4 Chatbot project are documented in this file.

The format follows the principles of **Keep a Changelog**.

---

## [2.0.0] - MK II Stable — July 2026

### Added

#### Artificial Intelligence

- Modular AI architecture
- AIService orchestration layer
- LLMService abstraction
- Provider-based LLM architecture
- GeminiProvider
- OllamaProvider
- BaseProvider interface
- Retrieval-Augmented Generation (RAG)
- PromptBuilder service
- Emotion-aware prompting
- Language-aware prompting
- Dynamic system prompts
- Conversation context support
- AI pipeline performance logging

#### Natural Language Processing

- English Emotion Recognition Model (EERM)
- Emotion detection
- Language detection
- Safety validation
- Crisis detection
- Emotion confidence scoring
- Negative sentiment detection
- English language support
- Filipino language detection
- Taglish language detection

#### Student Features

- AI Guidance Chat
- Guidance Office information retrieval
- Appointment booking
- Conversation export
- Responsive chatbot interface

#### Staff Features

- Guidance dashboard
- Chat takeover
- Appointment management
- Student concern monitoring

#### Backend

- Modular service architecture
- Environment-based configuration
- Provider switching
- Centralized AI initialization
- Performance monitoring
- Improved error handling

#### Documentation

- Complete project README
- Project Architecture documentation
- Dataset Documentation
- Preprocessing Pipeline documentation
- Model Architecture documentation
- API Integration guide
- Deployment Guide
- Future Work roadmap
- Design Decisions documentation
- CTRL4 Bible
- English model documentation
- Filipino model roadmap
- CHANGELOG

---

### Changed

#### Artificial Intelligence

- Replaced direct Gemini implementation with a provider-based architecture.
- Redesigned the AI pipeline into modular services.
- Moved prompt construction to the PromptBuilder service.
- Integrated Retrieval-Augmented Generation (RAG) into response generation.
- Performed safety validation before LLM generation.
- Incorporated emotion detection into prompt engineering.
- Integrated language detection into response generation.

#### Frontend

- Updated branding from Holy Angel University to the School of Computing.
- Updated the user interface color palette from red to orange.
- Improved chatbot interface.
- Improved dashboard layout.
- Improved appointment management interface.

#### Backend

- Improved project folder organization.
- Separated AI services from LLM provider implementations.
- Centralized application configuration.
- Improved AI service initialization and dependency management.

---

### Fixed

- HTTP 500 errors during AI generation failures.
- Duplicate AI pipeline performance logs.
- Gemini provider initialization issues.
- Ollama provider integration issues.
- Prompt generation consistency.
- Exception handling across AI services.
- Response generation reliability.
- AI pipeline logging output.

---

### Removed

- Rule-based chatbot responses.
- Legacy GeminiService implementation.
- Prototype AI orchestration logic.
- Hardcoded chatbot responses.
- Deprecated MK I placeholder comments.
- Legacy Holy Angel University branding assets.

---

## [1.0.0] - MK I — June 2026

Initial prototype release.

### Added

#### Artificial Intelligence

- Google Gemini integration
- Basic AI chatbot implementation

#### Student Features

- Student authentication
- Chat interface
- Guidance Office FAQ
- Appointment prototype

#### Frontend

- Holy Angel University branding
- Red user interface theme
- Initial dashboard

#### Backend

- Flask backend
- Basic authentication
- Initial chatbot routing