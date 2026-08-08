# Changelog

All notable changes to the CTRL4 Chatbot project are documented in this file.

The format follows the principles of **Keep a Changelog**.

---

## [1.0.6] - MK III Final Release — August 2026

### Added

- Added final release documentation alignment across README, architecture
  references, deployment guides, and user documentation.
- Added final environment configuration reference through the updated
  `.env.example`.
- Added finalized release references and repository documentation consistency
  for CTRL4 Chatbot MK III.

### Changed

- Finalized the CTRL4 Chatbot MK III release state after documentation review,
  repository cleanup, and release validation.
- Updated release references from v1.0.5 to v1.0.6 across project documentation.
- Updated final deployment and configuration references based on the validated
  local development environment.
- Preserved unvalidated startup hardening changes as archival material and
  excluded them from the final released system.

### Verified

- Completed final regression validation for authentication, security,
  conversation finalization, documentation contracts, and system workflows.
- Verified release documentation consistency with the implemented MK III
  architecture.
- Verified GitHub release tagging and repository state for the final release.

### Notes

- This release represents the finalized CTRL4 Chatbot MK III implementation.
- Historical MK I and MK II changes remain preserved in previous changelog
  entries.

---

## [Unreleased] - MK III documentation finalization

### Changed

- Added a student-only Terms and Conditions acknowledgement before chatbot
  access. Acceptance is required for each server-side session; declining ends
  the session.
- Documented the validated local host default (`127.0.0.1:5001`) and opt-in
  `CTRL4_HOST=0.0.0.0` Tailscale/LAN demonstration binding.
- Aligned current references with the MK III database audit and cleanup state,
  deferred migration/index work, staff privacy-safe case views, and the
  English-focused emotion-model limitation for Filipino/Taglish input.
- Recorded that the startup auto-setup hardening patch is preserved but
  unvalidated and is not part of the released system.

---

## [3.0.0] - CTRL4 Chatbot MK III v1.0 — August 2026

### Added

- Completed the authenticated chatbot and internal Conversation Intelligence
  pipeline for intent, emotion, topic, metadata, language, summaries, safety,
  retrieval, prompting, and escalation handling.
- Completed Appointment Management with dynamic program-based counselor routing,
  normalized start-time conflict handling, schedule and availability checks,
  canonical lifecycle management, student replacement rescheduling, and
  persistent in-app notifications.
- Added Guidance case-management workflows: flagged cases, dedicated counselor
  notes, referrals and histories, interventions and histories, confidential
  case handling, and the privacy-projected student case-status dashboard.
- Added staff aggregate analytics for appointments, chatbot activity, counselor
  workload, and flagged cases, plus Reports & client-side CSV export.

### Changed

- Standardized completed application workflows around the implemented Route →
  Service → Database architecture, server-side sessions, role boundaries, and
  established response envelopes.
- Added atomic database-backed active-slot persistence for appointment conflict
  protection without introducing counselor ownership or duration assumptions.
- Normalized current implementation branding, release documentation, API
  reference, installation/deployment guidance, and student, staff, and
  administrator user guides to CTRL4 Chatbot MK III.

### Verified

- Completed System Integration Testing, Security & Privacy Testing, and
  Performance & Reliability Testing infrastructure and regression coverage.
- Completed Deployment Preparation, current-reference documentation review,
  final release audit, and repository cleanup of confirmed legacy artifacts.
- Preserved historical MK II changelog history, roadmap material, and model or
  training provenance as archival records.

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

- Introduced provider-based LLM architecture.
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
- Legacy chatbot response handling.
- Prototype AI orchestration logic.
- Hardcoded chatbot responses.
- Deprecated MK I placeholder comments.
- Legacy Holy Angel University branding assets.
- Chat takeover workflow from MK I.

---

## [1.0.0] - MK I — June 2026

Initial prototype release.

### Added

#### Artificial Intelligence

- Basic chatbot implementation

#### Student Features

- Student authentication
- Chat interface
- Guidance Office FAQ
- Appointment prototype

#### Staff Features

- Guidance dashboard
- Chat takeover
- Student concern monitoring

#### Frontend

- Holy Angel University branding
- Red user interface theme
- Initial dashboard

#### Backend

- Flask backend
- Basic authentication
- Initial chatbot routing