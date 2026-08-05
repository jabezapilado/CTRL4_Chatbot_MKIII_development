# CTRL4 MK II - BACKEND IMPLEMENTATION PLAN

> **Historical planning document.** Current frozen implementation references:
> [Project Context](../architecture/project_context.md) and
> [Project Architecture](../architecture/project_architecture.md).

> This document defines the backend implementation roadmap of CTRL4 MK II.
>
> It translates the approved system architecture into backend modules and implementation phases.

---

# PURPOSE

The Backend Implementation Plan serves as the implementation reference for the CTRL4 MK II backend.

Unlike the architecture documents, this document focuses on how the system will be developed while remaining consistent with the approved architecture.

---

# IMPLEMENTATION PHILOSOPHY

The backend follows a layered architecture.

Business rules are separated from database operations to improve maintainability, scalability, and testing.

The backend is organized into:

- API Routes
- Services
- Validators
- Database Layer
- Utility Modules

---

# BACKEND ARCHITECTURE

```text
Frontend
        │
        ▼
API Routes
        │
        ▼
Conversation Session Manager
        │
        ▼
Service Layer
        │
        ▼
Validation Layer
        │
        ▼
Database Layer
        │
        ▼
SQLite Database
```

---

# PROJECT STRUCTURE

```text
backend/
│
├── server/
│
├── routes/
│     auth.py
│     appointments.py
│     chatbot.py
│     students.py
│     counselors.py
│     settings.py
│
├── services/
│     appointment_service.py
│     chatbot_service.py
│     conversation_session_service.py
│     counselor_service.py
│     summary_service.py
│
├── validators/
│     appointment_validator.py
│     auth_validator.py
│
├── utils/
│     datetime_utils.py
│     response.py
│
├── db.py
│
└── config.py
```

---

# IMPLEMENTATION PHASES

## Phase 1

Authentication

- Login
- JWT Authentication
- Role Verification
- Session Validation

---

## Phase 2

Appointment Engine

- Appointment Validation
- Conflict Detection
- Counselor Assignment
- Appointment Creation
- Appointment Updates
- Appointment Cancellation
- Appointment Rescheduling

---

## Phase 3

Conversation Intelligence

- Conversation Processing
- Active Conversation Session
- Conversation Restoration
- Session-Based Conversation Persistence
- Emotion Detection
- Intent Detection
- Topic Classification
- AI Counselor Intake Summary
- Automatic Conversation Deletion
- Session Cleanup

The Conversation Session Manager is responsible for preserving active conversations during an authenticated session, restoring conversations after page navigation or refresh, and cleaning up temporary conversation data after AI summary generation.

---

## Phase 4

Student Case Management

- Case Generation
- Counselor Notes
- Follow-up Recommendations
- Case Resolution

---

## Phase 5

Guidance Office Operations

- Appointment Settings
- Counselor Settings
- Office Settings
- Reports
- Analytics

---

## Phase 6

System Administration

- Account Management
- Access Control
- Role Management
- Authentication Settings

---

# CODING STANDARDS

The backend shall follow these principles:

- Thin API routes.
- Business logic belongs in services.
- Validation is centralized.
- Database access remains inside `db.py`.
- Every endpoint returns a consistent JSON response.
- Business rules must follow the approved architecture documents.
- Conversation session management shall remain separate from appointment business logic.
- Appointment validation and chatbot appointment requests shall use the same Appointment Service.
- Temporary conversation persistence shall never be treated as permanent storage.

---

# DEVELOPMENT ORDER

```text
Authentication
        ↓
Appointment Engine
        ↓
Conversation Session Manager
        ↓
Conversation Intelligence
        ↓
Student Case Management
        ↓
Guidance Office Operations
        ↓
System Administration
```

---

# IMPLEMENTATION RULES

The following implementation decisions are FINAL:

- Business logic shall not be written directly inside API routes.
- Database operations shall be centralized.
- Validation shall occur before any database transaction.
- Services shall contain all business rules.
- Architecture documents (00–05) remain the source of truth.
- This document defines how those architectural decisions are implemented.
- Active conversations shall be restored automatically while the authenticated session remains valid.
- Conversation finalization shall generate an AI Counselor Intake Summary before deleting temporary conversation data.
- The Appointment Engine shall serve both the AI Guidance Chatbot and the Appointment Form.
