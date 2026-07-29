# CTRL4 Chatbot MK III Roadmap

> Internal Development Roadmap
>
> Base Version: MK II Stable (v2.0)
>
> Status: Planning

---

# Vision

CTRL4 Chatbot MK III aims to evolve beyond a traditional AI chatbot into a multilingual, emotionally intelligent, counselor-assisted guidance platform.

The system will combine multiple AI models, Retrieval-Augmented Generation (RAG), multilingual NLP, counseling intelligence, and administrative tools to support both students and Guidance Office personnel.

---

# Core Design Philosophy

Unlike conventional AI chatbots, CTRL4 follows a modular architecture where every AI component performs a specialized responsibility.

Student Message

↓

Language Detection

↓

Emotion Detection

↓

Intent Detection

↓

Risk Detection

↓

Knowledge Retrieval (RAG)

↓

Prompt Engineering

↓

Large Language Model

↓

Student Response

↓

Counselor Escalation (if necessary)

This modular approach improves explainability, scalability, maintainability, and future extensibility.

---

# Phase 1 — Multilingual AI

## Filipino Emotion Recognition Model (FERM)

Priority: ★★★★★

Develop a dedicated transformer-based emotion recognition model for Filipino.

Tasks

- Collect Filipino emotion datasets
- Build preprocessing pipeline
- Standardize Filipino emotion taxonomy
- Label mapping
- Fine-tune DistilBERT
- Evaluate performance
- Model Card
- Training Log
- Evaluation Report

Output

FERM Version 1

---

## Taglish Emotion Recognition

Develop a model capable of understanding mixed English–Filipino conversations.

Tasks

- Collect Taglish conversations
- Build synthetic dataset
- Fine-tune multilingual transformer
- Evaluate against English model

---

## Automatic Language Detection

Supported Languages

- English
- Filipino
- Taglish

Automatically route messages to the appropriate emotion recognition model.

---

# Phase 2 — Advanced Emotion Intelligence

## Expanded Emotion Taxonomy

Current

- Positive
- Neutral
- Anger
- Sadness
- Fear

Future

- Joy
- Love
- Hope
- Gratitude
- Stress
- Anxiety
- Burnout
- Confusion
- Loneliness
- Hopelessness
- Fear
- Anger
- Sadness
- Neutral
- Positive

---

## Multi-label Emotion Detection

Instead of predicting one emotion only,

Example

Sadness (81%)

Fear (14%)

Stress (5%)

---

## Confidence Calibration

Return

- Predicted Emotion
- Confidence Score
- Top 3 Predictions

---

# Phase 3 — Counseling Intelligence

## Intent Detection

Recognize

- Appointment Request
- Academic Concern
- Mental Health Concern
- Family Concern
- Relationship Concern
- Financial Concern
- Career Guidance
- General Inquiry

---

## Crisis Detection

Detect

- Suicide Ideation
- Self-harm
- Abuse
- Violence
- Emergency Situations

---

## Escalation Recommendation Engine

Provide

- Risk Level
- Reason
- Recommended Counselor Action

---

# Phase 4 — Advanced RAG

## Hybrid Retrieval

Combine

- Keyword Search
- Vector Search
- Metadata Filtering

---

## Semantic Chunking

Replace fixed chunking with

- Semantic chunking
- Heading-aware chunking
- Paragraph-aware chunking

---

## Cross-Encoder Reranking

Retrieve

↓

Rerank

↓

Generate Response

---

## Knowledge Base Versioning

Track

- Policy revisions
- Effective dates
- Knowledge versions

---

# Phase 5 — Conversation Intelligence

## Long-Term Memory

Remember

- Previous concerns
- Previous appointments
- Conversation context

while respecting privacy policies.

---

## AI Conversation Summary

Automatically generate

- Conversation Summary
- Main Concerns
- Detected Emotions
- Follow-up Suggestions

---

## Emotional Timeline

Display emotional trends over time.

Weekly

Monthly

Semester

Academic Year

---

# Phase 6 — Analytics

Dashboard Metrics

- Daily Conversations
- Emotion Distribution
- Language Distribution
- Appointment Requests
- Escalations
- Average Response Time
- AI Confidence

---

# Phase 7 — AI Infrastructure

## Model Registry

Manage

- English Emotion Model
- Filipino Emotion Model
- Intent Model
- Risk Model

---

## Automatic Model Loading

Load models dynamically using a model registry.

---

## Model Versioning

Support

- v1
- v2
- v3

without backend code modifications.

---

# Phase 8 — LLM Improvements

## Streaming Responses

Generate responses token-by-token.

---

## Dynamic Prompt Engineering

Prompts adapt according to

- Emotion
- Language
- Intent
- Risk
- Knowledge Context

---

## Additional Providers

Support

- Google Gemini
- Ollama
- OpenAI
- Anthropic
- DeepSeek
- Groq
- OpenRouter

---

# Phase 9 — Student Portal

Features

- Conversation History
- Appointment History
- Dark Mode
- Voice Input
- Voice Output
- Suggested Questions
- File Upload
- Typing Indicator
- Emotion History

---

# Phase 10 — Research

Experiments

Compare

- English vs Filipino
- RAG vs No RAG
- Gemini vs Ollama
- DistilBERT vs ModernBERT
- DistilBERT vs RoBERTa
- DistilBERT vs DeBERTa
- Single-label vs Multi-label

Evaluation

- Accuracy
- Precision
- Recall
- F1 Score
- Latency
- Throughput
- User Satisfaction
- Counselor Acceptance

---

# Phase 11 — Staff Dashboard (Guidance Counselor)

Purpose

Provide counselors with AI-assisted student support.

Features

## Dashboard

- Active Conversations
- Today's Appointments
- Students Waiting
- High-Risk Alerts
- Emotion Distribution
- Counselor Schedule

---

## Student Management

- Student Profiles
- Conversation History
- Appointment History
- Emotional Timeline
- Case Notes
- Follow-up Records

---

## AI Assistance

- Live Chat Takeover
- AI Conversation Summary
- AI Suggested Responses
- AI Recommendations
- Escalation Recommendations

---

## Appointment Management

- Calendar View
- Weekly Schedule
- Monthly Schedule
- Reschedule
- Counselor Availability

---

## Reports

- Counseling Reports
- Student Reports
- Emotion Reports

---

## Notifications

- High-Risk Alerts
- Appointment Requests
- Escalation Requests
- New Conversations

---

## Wellness Profile

Maintain a long-term student wellness profile including

- Emotional Trends
- Frequently Discussed Concerns
- Appointment History
- Counselor Notes
- Risk History
- AI Summaries

---

# Phase 12 — Admin Dashboard (System Administration)

Purpose

Manage the CTRL4 platform.

Features

## System Dashboard

- Server Status
- Database Status
- AI Status
- Storage Usage
- Active Users

---

## User Management

- Students
- Staff
- Administrators
- Roles
- Permissions
- Password Reset

---

## AI Management

- Active Provider
- Model Selection
- Prompt Management
- AI Configuration

---

## Knowledge Base Management

- Upload Documents
- Remove Documents
- Edit Documents
- Rebuild FAISS Index
- Document Versioning

---

## Model Management

Manage

- EERM
- FERM
- Intent Model
- Risk Model

View

- Version
- Accuracy
- Training Date
- Status

---

## RAG Settings

Configure

- Embedding Model
- Top K
- Similarity Threshold
- Chunk Size
- Chunk Overlap

---

## Analytics

- AI Usage
- Language Usage
- Emotion Statistics
- Response Times
- Provider Usage
- System Performance

---

## Audit Logs

Track

- Login Activity
- AI Requests
- Database Changes
- Knowledge Base Updates
- Administrative Actions

---

## Database Management

- Backup
- Restore
- Export
- Maintenance

---

## System Settings

- Environment Variables
- API Keys
- Branding
- Maintenance Mode
- Email Configuration

---

# User Roles

## Student

- AI Chat
- Appointment Booking
- View Own Conversations
- Export Own Conversations
- Profile Management

---

## Staff (Guidance Counselor)

- Student Management
- Counseling Sessions
- AI Assistance
- Chat Takeover
- Case Notes
- Reports
- Appointment Management

---

## Administrator

- Full System Access
- User Management
- AI Management
- Knowledge Base Management
- System Configuration
- Analytics
- Database Management

---

# Long-Term Vision (MK IV)

Future research directions include

- Multimodal AI (Text, Voice, Images)
- Voice Conversations
- Counselor AI Copilot
- Personalized Well-being Insights
- Mobile Applications
- University System Integration
- Cloud Deployment
- Privacy-Preserving Learning
- Federated Learning
- Anonymous Institutional Analytics

---

# Development Order

1. Filipino Emotion Recognition Model (FERM)
2. Multilingual Pipeline
3. Taglish Support
4. Intent Detection
5. Crisis Detection
6. Escalation Engine
7. Enhanced RAG
8. Conversation Memory
9. Counselor Workspace
10. Analytics Dashboard
11. AI Infrastructure
12. LLM Improvements

---

# Project Goal

The long-term objective of CTRL4 is not simply to build another chatbot, but to create a modular AI-powered Guidance Office platform that responsibly combines multilingual natural language understanding, emotion recognition, retrieval-augmented generation, counselor-assisted decision support, and modern software engineering principles to improve student support while ensuring that human guidance counselors remain central to all critical decisions.