# CTRL4 Chatbot MK III — Project Context

## Status and authority

CTRL4 Chatbot MK III is an AI-powered Guidance Office support system for Holy Angel University students. It combines authenticated chatbot conversations, appointment management, account administration, conversation escalation, and staff-facing operational views.

Sprints 3–10 are complete and frozen. This document captures the implemented architecture for future contributors. When an older plan differs from an intentional frozen implementation, the current implementation is authoritative unless the project owner explicitly overrides it.

## MK III operational baseline

The validated local database is XAMPP MariaDB `soc_chatbot`. The MK III audit
found `db.py`, `schema.sql`, and the live schema structurally aligned. The
local demo cleanup removed chat/case test residue after backup verification and
preserved all foundation data, including accounts, settings, program catalog,
FAQs, appointment availability, and staff assignment/room/schedule metadata.

No versioned migration framework or new index set is part of this release. The
saved startup auto-setup hardening patch is unvalidated and intentionally not
applied. Treat generated RAG artifacts as protected operational assets.

## Project map

| Area | Location | Responsibility |
| --- | --- | --- |
| Application | `backend/app.py`, `backend/server/` | Flask configuration, HTTP application, sessions |
| Routes | `backend/server/routes/`, `backend/server/auth.py` | HTTP, RBAC, sessions, logging, response serialization |
| Services | `backend/server/services/` | Framework-agnostic business rules and AI orchestration |
| Database | `backend/server/db.py`, `backend/sql/schema.sql` | MySQL access, parameterized persistence, integrity safeguards |
| Frontend | `frontend/templates/`, `frontend/static/` | HTML/CSS/JavaScript presentation |
| AI assets | `ai_engine/` | Emotion assets, training utilities, RAG knowledge records |
| Scripts | `backend/scripts/`, `scripts/` | Bootstrap, database setup, knowledge ingestion |

The stack uses Flask, server-side sessions, MySQL/MariaDB, HTML/CSS/JavaScript, FAISS-backed RAG, and Gemini or Ollama through the LLM provider abstraction.

## Core architecture

```text
Route → Service → Database
```

- **Routes** own HTTP parsing, RBAC checks, Flask session handling, logging, status codes, and JSON serialization.
- **Services** own business validation, privacy projection, appointment policy, notifications, Conversation Intelligence, and AI orchestration. They must not manipulate Flask `session`, `request`, or `jsonify`.
- **Database helpers** own parameterized queries, generic retrieval, persistence, and defensive integrity safeguards. They do not make business decisions such as appointment availability or counselor routing.

`backend/server/services/__init__.py` is the central service-composition point for long-lived AI services.

## Authentication and RBAC

Authentication uses Flask **server-side CacheLib sessions**, not JWT. `auth.py` is the single owner of session creation and clearing. Successful login clears and rotates the prior session, sets it permanent, and stores the authenticated user in `session["hau_user"]`. The browser receives only an opaque session identifier; session payload and escalation markers remain server-side. Cookies are `HttpOnly`, `SameSite=Lax`, configurable `Secure`, and expire after eight hours. The currently supported topology is one application instance; horizontal scaling requires an approved shared session backend.

| Role | Authority |
| --- | --- |
| `student` | Own chatbot activity, own appointments, own notifications |
| `staff` | Guidance operations, routed appointments, notes, settings, summaries, escalations |
| `admin` | Account management only; no guidance-specific counseling data or appointment-state authority |

Route RBAC reuses `require_login`, `require_role`, and `require_any_role`. ITSS administrators must not be granted guidance-specific counseling access.

## API and validation conventions

Success responses use the existing envelope:

```json
{"success": true, "message": "...", "data": {}}
```

Failures preserve existing status codes/messages and normally use:

```json
{"success": false, "message": "...", "errors": null}
```

Business validation belongs in services. Database uniqueness, defensive normalization, automatic account-number generation, foreign keys, and enums are persistence safeguards that remain in place. Existing validation order and externally visible errors are compatibility requirements.

## Frozen account-management decisions — Sprint 3

The account module reuses generic account primitives in `db.py`: `create_account`, `fetch_account_by_id`, `list_accounts`, and `update_account_fields`. Role-specific field validation stays in `account_service.py`.

- Student updates accept only approved student profile fields and reject unsupported fields.
- Staff profile metadata includes assigned programs, office, support statement, consultation rooms, and consultation schedules; this metadata alone is not appointment-engine behavior.
- Administrator accounts cannot store student/staff/counselor metadata or account numbers. Administrators cannot deactivate themselves.
- The administrative account listing supports optional `q` with existing role/status filters. It searches names and emails for every account role, plus the appropriate student or staff number where one exists.
- Duplicate email handling uses both a service pre-check and database uniqueness; persistence collisions map to the existing service-level duplicate-email error.

## Frozen appointment decisions — Sprint 4

`appointment_service.py` owns appointment policy; appointment routes remain HTTP/RBAC adapters and `db.py` remains persistence-only.

### Routing, conflicts, and validation

- Counselor routing is dynamic and program-based through `get_staff_by_program`. Every relevant booking operation uses the current first match. Counselor ownership is not persisted on an appointment and there is no fallback.
- Appointments persist only a date and start time; there is no authoritative duration/end-time contract. Conflict detection therefore compares normalized start-time equality on the same date—not interval overlap.
- Only `pending` and `confirmed` appointments block conflict creation.
- The final persistence recheck is atomic. The database transaction takes a bounded advisory lock derived from the normalized date/time key, rechecks blocking appointments, then inserts or rolls back. It prevents concurrent duplicate active bookings without storing counselor ownership or inventing an interval model.
- Counselor schedule validation uses only the routed counselor. Valid weekday grammar is `Monday`, `Monday-Friday`, or `Monday to Friday`; valid time grammar is a 12-hour range such as `7:00 AM - 5:00 PM`. Weekday ranges are inclusive; time windows are start-inclusive and end-exclusive. Invalid schedule metadata fails closed.
- Office availability is the generic settings value `appointmentAvailability`. It must contain exactly `officeAvailability`, `holidays`, `academicCalendarExclusions`, and `unavailableDates`. Office windows use the same grammar; exclusion dates are unique canonical `YYYY-MM-DD` values. Missing, malformed, partial, or invalid configuration fails closed. Descriptive `officeHours` remains informational only.

### Rescheduling and lifecycle

- Student rescheduling is replacement-then-cancel. A failed replacement must never cancel the original appointment.
- Students manage only their own pending appointments outside the one-hour modification deadline.
- The final persisted lifecycle is exactly: `pending`, `confirmed`, `cancelled`, `rejected`, `completed`.

```text
pending   → confirmed | rejected | cancelled
confirmed → completed | cancelled
cancelled, rejected, completed → terminal
```

- Assigned staff perform lifecycle transitions. Students retain their existing cancellation/reschedule endpoints. Administrators have no lifecycle authority. `confirmed → completed` requires non-empty counselor notes.
- Student-created/replacement appointments start `pending`; manual appointments start `confirmed`.

## Frozen notifications and frontend decisions — Sprint 5

Notifications are persistent, recipient-scoped, in-app only. They store a recipient, title, message, type, timestamp, and read state. Recipients mark them read explicitly; there is no deletion, expiration, email, SMS, push, browser notification, or reminder scheduling. Notification persistence is best-effort: it must not roll back an authoritative appointment action.

Appointment history privacy is service-owned. Students do not receive `counselor_notes`; authorized staff do. Staff dashboard search works only over already authorized appointment data. The staff month calendar is read-only and uses the staff appointment dataset. Student appointment management reuses the existing listing, cancellation, and replacement-rescheduling APIs.

Dynamic data in appointment, student, notification, and conversation rendering must use DOM APIs and `textContent`, not untrusted `innerHTML` interpolation.

## Frozen Conversation Intelligence and privacy — Sprint 6

Conversation persistence/finalization and privacy projection are service-owned by `conversation_service.py`. Staff views exclude internal linkage fields such as account IDs and escalation summary IDs. Conversation summaries are structured, counselor-oriented, confidential, non-diagnostic, and do not rewrite raw conversation history.

Conversation Intelligence results are internal service data:

| Component | Canonical values |
| --- | --- |
| Intent | `greeting`, `appointment_booking`, `appointment_cancellation`, `appointment_rescheduling`, `appointment_history`, `office_hours`, `faq`, `emergency`, `unknown` |
| Normalized emotion | `neutral`, `positive`, `negative`, `distressed`, `crisis` |
| Topic | `appointments`, `academics`, `counseling`, `mental_health`, `school_services`, `general_inquiry` |
| Metadata | `student_number`, `appointment_date`, `appointment_time`, `office`, `counselor`, `category` |
| Language | `english`, `filipino`, `taglish`, with existing fallback for unknown input |

Metadata extraction is read-only: it captures only explicit values, validates ISO dates, normalizes explicit 12/24-hour times, and does not resolve counselor entities. A conversation is eligible for escalation when existing AI escalation is true or normalized emotion is `crisis`/`distressed`. The session marker clears only after successful finalization; client-provided flags cannot suppress it.

## Frozen chatbot and safety decisions — Sprint 7

The common chatbot pipeline is:

```text
Language detection
→ SafetyService
→ Conversation Intelligence
→ RAG when applicable
→ PromptBuilder
→ LLM provider
→ ResponseSafetyService
```

- `SafetyService` remains authoritative for pre-generation crisis/diagnosis handling and escalation. It receives detected language for fixed safety replies.
- `LanguageService` supports English, Filipino, and Taglish. Shared lexicon vocabulary is neutral evidence; Taglish requires exclusive evidence from both language vocabularies.
- The released emotion model is English-focused. Filipino/Tagalog and Taglish
  response/rule support does not establish equivalent emotion-classification
  accuracy.
- `RAGService` is the single retrieval component. It accepts read-only JSON, PDF, DOCX, TXT, and Markdown knowledge records while preserving thresholding, ranking, de-duplication, and source attribution.
- `PromptBuilder` receives already computed Conversation Intelligence outputs; it does not recompute them.
- `ResponseSafetyService` deterministically validates final generated text. It replaces the entire response, never partially redacts it, for exactly: medical diagnosis, treatment/prescription instructions, self-harm/violence encouragement or procedures, prompt disclosure, protected-information disclosure, and unsupported official Guidance Office claims. It logs only that a replacement occurred, never blocked generated text. It does not alter escalation behavior.
- `/chat` and `/chat/finalize` retain their public contracts. Chat inquiry persistence is owned by `conversation_service.py`, not the route.

## Sprint summary

| Sprint | Frozen outcome |
| --- | --- |
| 1–2 | Existing response/validation conventions, server sessions, and RBAC baseline. |
| 3 | Account management, dynamic counselor program assignment, administrative account search, validation consolidation, and login-envelope consistency. |
| 4 | Appointment conflict/schedule/availability policy, student rescheduling confirmation, canonical lifecycle, and service consolidation. |
| 5 | Appointment history privacy, dashboard search/XSS remediation, notifications, staff calendar, and student appointment management. |
| 6 | Intent, emotion, topic, metadata, summaries, and conversation privacy projection. |
| 7 | Chat integration layering, JSON RAG records, structured prompt context, escalation workflow, response safety, and multilingual support. |
| 8 | Flagged-case management: dedicated counselor notes, referrals, interventions, confidentiality, and the student case-status privacy projection. |
| 9 | Staff aggregate analytics for appointments, chatbot activity, counselor workload, and flagged cases; reports/CSV export and analytics overview. |
| 10 | System integration, security/privacy, performance/reliability, deployment preparation, and current-reference documentation. |

## Sprint 8 — case management

Case-management operations are staff-only and build on flagged conversation
summaries. Dedicated counselor notes persist separately. Referrals and
interventions retain their append-only histories; confidentiality retains a
current state and append-only history. Student case status is a strict
privacy projection: it does not expose summaries, notes, reasons, referrals,
interventions, confidentiality data, or internal identifiers.

## Sprint 9 — analytics and reports

Analytics are read-only and aggregate-only. Appointment analytics use the
authenticated staff member's existing authorized appointment/program scope,
including current dynamic-routing counselor counts only. Counselor workload
uses that appointment scope plus the authenticated staff member's persisted
referral/intervention ownership; it does not infer flagged-case reviewer
ownership. Chatbot analytics report only persisted, truthfully representable
values: total chatbot messages, time trends, finalization/escalation counts,
persisted `emotion_result` distribution, and average finalized message count.
Flagged-case analytics are staff-wide aggregates and do not infer counselor
ownership. Reports reuse the four existing analytics APIs with one shared
optional date filter and client-side aggregate-only CSV export; PDF export is
not implemented.

## Sprint 10 — readiness, security, and deployment

Sprint 10 validated system integration and database synchronization, then
established server-side CacheLib sessions, protected-chat logging rules,
browser-persistence removal, and safe dashboard rendering. Appointment writes
now include the atomic database-backed normalized-slot conflict recheck noted
above. Deployment preparation made root `requirements.txt` the canonical
dependency source and documented explicit fresh-schema versus backup-first
compatibility upgrade paths. The current production topology is one Gunicorn
worker/application instance behind HTTPS; a shared session backend is required
before multi-instance deployment.

## Deferred work from completed reviews

These are recommendations only; they are not approved scope:

- Automated unit, integration, authenticated end-to-end, and frontend regression tests across accounts, appointments, notifications, conversations, and AI.
- Multilingual regression tests for ambiguous/shared vocabulary and corpus-based language evaluation.
- RAG index regeneration in a production embedding environment and real-model integration verification.
- Fake-LLM end-to-end prompt tests across Conversation Intelligence combinations.
- Frontend accessibility and test improvements.
- The pre-existing pending-appointment notes-control UX issue.
- Future conversation-session identifiers for parallel browser tabs.
- Summary-quality evaluation and explicitly approved privacy refinements.

## Required future-change workflow

1. Read the assigned GitHub issue and treat it as the sole implementation scope.
2. Audit current code for reusable route, service, database, and frontend pieces.
3. Design the smallest maintainable change; classify reuse, extension, new work, and out-of-scope work.
4. Implement only approved scope. Do not modify frozen work incidentally.
5. Review architecture, security, validation ownership, API compatibility, privacy, regression risk, duplicate/dead code, and scope adherence.
6. Verify at least:

```bash
python3 -m compileall backend/server
git diff --check
```

Run `node --check` for affected frontend JavaScript and focused checks for the changed business rule. Freeze only when no Category A findings remain.
