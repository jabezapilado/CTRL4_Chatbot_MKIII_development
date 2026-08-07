# CTRL4 Chatbot MK III — Current Project Architecture

> **Current reference.** This document describes the implemented system through
> Sprint 10. Start at the [documentation index](../README.md). For
> implementation constraints, read [AGENTS.md](../../AGENTS.md) and for frozen
> decisions, read [Project Context](project_context.md). Documents in
> [roadmap/](../roadmap/) are historical planning artifacts.

## Purpose and major domains

CTRL4 is an authenticated Guidance Office support system for Holy Angel
University. Its implemented domains are account management, appointments,
in-app notifications, chatbot conversations and finalization, flagged-case
management, counselor notes, referrals, interventions, confidentiality,
student case-status projection, and staff analytics/reports.

The stack is Flask, MySQL/MariaDB, server-side CacheLib sessions, a JavaScript
frontend, FAISS-backed retrieval, and Gemini or Ollama through the LLM provider
abstraction.

## System ownership

```text
Frontend → Route → Service → Database
```

| Layer | Owns | Must not own |
| --- | --- | --- |
| Frontend | Presentation, safe rendering, interaction, advisory checks | Authorization or authoritative business rules |
| Route | HTTP parsing, RBAC, Flask sessions, boundary logging, status codes, response serialization | Persistence orchestration or domain policy |
| Service | Validation, workflows, privacy projections, analytics aggregation, appointment rules, notifications, conversation and AI orchestration | Flask `session`, `request`, blueprints, or JSON serialization |
| Database | Parameterized retrieval/persistence, migrations, transactions, advisory locking, integrity safeguards | API behavior, counselor routing, or booking policy |

`backend/server/services/__init__.py` is the central composition point for
long-lived AI services. Routes reuse registered services instead of constructing
parallel pipelines.

## Authentication and RBAC

Authentication uses Flask **server-side** sessions. `backend/server/auth.py`
is the only session owner: it clears/rotates a session after login, stores the
authenticated user as `hau_user`, marks the session permanent, and clears it
on logout. Route guards reuse `require_login`, `require_role`, and
`require_any_role`.

| Role | Implemented authority |
| --- | --- |
| Student | Own chatbot activity, appointments, notifications, and approved case-status projection |
| Guidance staff | Staff appointment, conversation, case-management, settings, analytics, and reports workflows exposed by staff route guards and service checks |
| Administrator | Account management only |

Administrators do not have guidance-record, appointment-state, flagged-case,
counselor-note, referral, intervention, confidentiality, conversation,
escalation, or analytics authority.

## Appointments

Counselors are dynamically selected from a student's current program through
`get_staff_by_program`; appointments do **not** store counselor ownership and
there is no alternate-counselor fallback. The persisted model has a date and a
start time only, so conflict handling is same-date, normalized start-time
equality—not duration or interval-overlap logic.

The service performs early conflict validation for existing error precedence.
The final insert is atomic: the database transaction uses a bounded advisory
lock keyed by the normalized date/time, rechecks blocking appointments, then
inserts or rolls back. Only `pending` and `confirmed` block a slot. The
non-blocking states are `cancelled`, `rejected`, and `completed`. A conflict
returns HTTP `409` and exactly `This schedule is already taken.`

Appointment policy is service-owned:

- consultation schedules are checked only for the dynamically routed counselor;
- Guidance Office availability comes from `appointmentAvailability` settings
  and fails closed when invalid;
- students can cancel or replacement-reschedule only their own pending
  appointments outside the one-hour deadline;
- a replacement is created before its original is cancelled;
- student/replacement appointments start `pending`; manual appointments start
  `confirmed`; and
- lifecycle is `pending → confirmed/rejected/cancelled`, then
  `confirmed → completed/cancelled`; all other states are terminal. Completing
  a confirmed appointment requires nonblank counselor notes.

## Conversations, cases, and notifications

Raw message history is used only for the active interaction and finalization;
it is not persisted as a transcript. Finalization persists the existing
counselor-oriented summary and approved metadata, and may create one
summary-linked escalation. Staff-only case workflows build on flagged
summaries: dedicated counselor notes, internal referrals and append-only
history, interventions and append-only history, and current confidentiality
state with append-only history. Student case status is a privacy-projected,
generic status view only.

The staff dashboard uses privacy-safe summaries rather than raw transcripts.
Inbox presents one current summary item per student/case priority, Flagged
Cases presents active pending flagged cases, and reviewed cases remain available
through Reviewed Case History. Case Details presents Detected Emotion and Safety
Risk as distinct fields. Crisis or sensitive cases remain pending until review;
routine follow-up must not erase an unresolved flagged case.

Notifications are persistent, recipient-scoped, in-app records. A recipient
marks a notification read explicitly. Notification writes are best-effort and
never roll back an authoritative appointment action.

## AI and chatbot pipeline

```text
Language Detection
→ SafetyService pre-generation checks
→ Conversation Intelligence (intent, emotion, topic, metadata)
→ RAG
→ PromptBuilder
→ LLM generation
→ ResponseSafetyService
→ response/finalization/escalation handling
```

Language support is English, Filipino, and Taglish. Shared lexicon terms are
neutral evidence; Taglish requires exclusive evidence from both languages.
The released emotion model is English-focused; Filipino/Tagalog and Taglish
emotion classification remains a limitation rather than a claim of equivalent
model validation.
SafetyService is authoritative for pre-generation crisis and diagnosis
handling. ResponseSafetyService validates generated output and replaces an
unsafe reply as a whole; it does not change escalation policy. Conversation
Intelligence outputs are internal unless an existing API exposes a current
field. The chatbot is not a diagnostic or treatment service.

## Analytics and reports

Analytics are read-only and aggregate-only. Appointment and counselor workload
analytics use the authenticated staff member's authorized appointment/program
scope. Referrals and interventions use persisted staff ownership. Chatbot and
flagged-case analytics retain their existing staff-wide aggregate scopes. The
Reports view reuses the four analytics APIs with one shared optional date
range and produces client-side CSV from already-authorized aggregate data.

For endpoint detail, see the [API Reference](api_reference.md). For deployment,
see the [Deployment Guide](../deployment/deployment_guide.md).
