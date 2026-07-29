# CTRL4 MK II - SYSTEM PILLARS

> This document defines the five core architectural pillars of CTRL4 MK II.
>
> These pillars serve as the foundation for the system architecture, feature planning, user interface, backend implementation, database design, and thesis documentation.

---

# OVERVIEW

CTRL4 MK II is organized around five major pillars.

Every feature, workflow, page, API, database component, and future enhancement shall belong to one of these pillars.

These pillars provide the high-level structure of the entire Guidance Office Management System.

---

# 1. AI CHATBOT

## Summary

Serves as the primary interface where students access guidance information, ask inquiries, and request appointments through an intelligent conversational assistant.

### Includes

- Guidance-related Inquiries
- Knowledge Base (RAG)
- Frequently Asked Questions (FAQs)
- Guidance Services
- Academic Support
- Office Information
- Appointment Booking
- Real-time NLP Processing

---

# 2. CONVERSATION INTELLIGENCE

## Summary

Processes student conversations in real time to detect emotions, generate AI Counselor Intake Summaries, and protect privacy by automatically deleting raw conversations after processing.

### Includes

- Temporary Conversation Processing
- Emotion Detection
- Topic Classification
- Intent Detection
- Appointment Detection
- Flagged Case Detection
- AI Counselor Intake Summary
- Conversation Statistics
- Automatic Conversation Deletion
- Privacy-by-Design

---

# 3. STUDENT SUPPORT SERVICES

## Summary

Manages appointments, student cases, counselor interventions, and follow-up records to support the complete counseling workflow.

### Includes

- Appointment Management
- Student Case Management
- Counselor Notes
- Appointment History
- Follow-up Recommendations
- Resolved Cases
- Appointment Analytics

---

# 4. GUIDANCE OFFICE OPERATIONS

## Summary

Provides staff with tools to manage appointments, office settings, counselor configurations, reports, and analytics for efficient Guidance Office operations.

### Includes

- Guidance Office Information
- Appointment Settings
- Counselor Management
- Office Configuration
- Reports
- Analytics
- Flagged Case Monitoring

---

# 5. SYSTEM ADMINISTRATION

## Summary

Ensures secure system access through authentication, role-based access control, and account management for students, staff, and administrators.

### Includes

- Authentication
- Authorization
- Role-Based Access Control
- Account Management
- User Roles
- Permission Management
- System Access Management

---

# SYSTEM ARCHITECTURE

```text
                 CTRL4 MK II
 AI-Powered Guidance Office Management System
     with an Integrated Guidance Chatbot

                 ┌───────────────────────┐
                 │     AI Chatbot        │
                 └──────────┬────────────┘
                            │
                 ┌──────────▼────────────┐
                 │ Conversation          │
                 │ Intelligence          │
                 └──────────┬────────────┘
                            │
                 ┌──────────▼────────────┐
                 │ Student Support       │
                 │ Services              │
                 └──────────┬────────────┘
                            │
                 ┌──────────▼────────────┐
                 │ Guidance Office       │
                 │ Operations            │
                 └──────────┬────────────┘
                            │
                 ┌──────────▼────────────┐
                 │ System                │
                 │ Administration        │
                 └───────────────────────┘
```

---

# ARCHITECTURAL RULE

The following architectural decisions are FINAL:

- Every feature shall belong to one of the five system pillars.
- Every page shall support one primary pillar.
- Every backend service shall be categorized under one pillar.
- Every database component shall support one or more pillars.
- Future enhancements shall follow the same architectural organization.
- The five pillars serve as the official architectural foundation of CTRL4 MK II.

---

# THESIS REMINDER

Never forget:

> CTRL4 MK II is an AI-Powered Guidance Office Management System with an Integrated Guidance Chatbot. Its architecture is organized around five core pillars: AI Chatbot, Conversation Intelligence, Student Support Services, Guidance Office Operations, and System Administration.