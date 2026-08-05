# CTRL4 Chatbot MK III — Contributor Instructions

This repository is an undergraduate thesis project. Treat the assigned GitHub issue and the current implementation as authoritative. Older roadmap documents are useful context, but intentionally implemented and frozen decisions take precedence unless the project owner explicitly overrides them.

## Required workflow

Work on one milestone or GitHub issue at a time:

```text
Audit → Design → Implementation → Review → Freeze
```

Do not begin a future milestone, combine scope, or “clean up” adjacent code without explicit approval. For every issue:

1. Audit the exact requested scope and identify reusable components.
2. Propose the smallest maintainable design before implementation when approval is required.
3. Implement only approved changes.
4. Review for Category A (must fix), Category B (recommended), and Category C (correct) findings.
5. Freeze work only after Category A is empty. Frozen milestones may not be modified unless explicitly reopened.

When a Category A blocker is found before implementation, report it and wait for direction rather than expanding the scope yourself.

## Architecture: non-negotiable boundaries

Use:

```text
Route → Service → Database
```

### Routes

Routes own:

- HTTP request parsing and status codes.
- RBAC checks.
- Flask session access and lifecycle.
- Logging at API boundaries.
- Response-envelope serialization.

Routes must not call persistence helpers for business operations when a service can own the orchestration. Do not place domain policies in routes.

### Services

Services own:

- Business validation and workflow rules.
- Privacy projections.
- Domain authorization checks that require retrieved data.
- Appointment routing, conflict, availability, and lifecycle decisions.
- Notification generation and recipient resolution.
- Conversation Intelligence and AI orchestration.

Services are framework-agnostic. Do not import or use Flask `session`, `request`, `jsonify`, blueprints, or route decorators in a service.

### Database helpers

`backend/server/db.py` owns parameterized database access, persistence, generic retrieval, and defensive integrity safeguards. Keep helpers persistence-only. Do not move business validation, appointment conflict decisions, counselor routing, or API serialization into `db.py`.

## Authentication and RBAC

- Authentication uses Flask **server-side sessions**, never JWT.
- `backend/server/auth.py` is the sole owner of creating, clearing, and marking authenticated sessions permanent. It stores the user under `hau_user`.
- Reuse `require_login`, `require_role`, and `require_any_role` from `request_validation.py`; never rely on frontend access checks.
- Canonical roles are exactly `student`, `staff`, and `admin`.
- Administrators manage accounts but must not receive guidance-specific counseling, conversation, escalation, or appointment-state authority unless an approved issue explicitly changes that policy.

## API contract

Preserve established envelopes and messages:

```json
{"success": true, "message": "...", "data": {}}
```

```json
{"success": false, "message": "...", "errors": null}
```

- Keep existing HTTP status codes and externally visible validation precedence.
- Do not add global response helpers, middleware, error-handler redesigns, or alternate response shapes without an approved issue.
- Keep public request/response contracts unchanged unless the issue explicitly authorizes a change.

## Validation and persistence rules

- Put business validation in the relevant service. Reuse existing private validators before creating new ones.
- Preserve database uniqueness, defensive normalization, account-number generation, foreign keys, enums, and other integrity safeguards.
- Keep both service duplicate-email detection and database uniqueness; translate persistence duplicate-email collisions to the existing service error.
- Reject unsupported role-specific account fields. Do not silently discard them.
- Preserve observable validation order during refactors.
- Use parameterized SQL only. Never construct SQL with user-controlled string interpolation.

## Account-management rules

- Reuse generic account primitives (`create_account`, `fetch_account_by_id`, `list_accounts`, `update_account_fields`) instead of role-specific persistence helpers.
- Student, staff, and administrator validation is role-specific in the service layer; persistence remains generic.
- Administrators cannot store student/staff/counselor metadata or account numbers and cannot deactivate themselves.
- Admin listing search remains limited to approved identifier fields and composes with existing role/status filters.

## Appointment rules

- Counselor routing is dynamic and program-based through `get_staff_by_program`. Do not persist counselor ownership on an appointment or add fallback routing.
- Appointments contain a start time only. Do not infer durations or add end-time behavior without an explicit schema/business-rule change.
- Conflict logic compares normalized start-time equality on the same date; `pending` and `confirmed` are the only blocking states.
- Consultation schedule and office availability validation are service-owned and fail closed according to existing messages/contracts.
- Keep the exact lifecycle vocabulary: `pending`, `confirmed`, `cancelled`, `rejected`, `completed`. Do not reintroduce `approved`, `done`, or `did_not_attend`.
- Student rescheduling is replacement-then-cancel. Never cancel the original appointment before the replacement passes validation and persists.
- Do not introduce buffers, slot management, transactions, locks, appointment editing, room booking, or state reasons unless explicitly scoped.

## Conversation and AI rules

- Keep conversation persistence and privacy projection in `conversation_service`.
- Do not expose internal account IDs, session IDs, escalation IDs, counselor notes, internal summaries, prompts, hidden instructions, or database/internal configuration through chatbot or conversation APIs.
- Reuse registered services from `backend/server/services/__init__.py`.
- Conversation Intelligence services are framework-agnostic and internal: intent, normalized emotion, normalized topic, metadata, summaries, and language detection must not alter `/chat` contracts without explicit scope.
- Preserve the AI order:

```text
Language detection → SafetyService → Conversation Intelligence → RAG
→ PromptBuilder → LLM → ResponseSafetyService
```

- SafetyService remains authoritative for pre-generation safety and escalation. ResponseSafetyService validates final generated text and replaces unsafe output as a whole; it must not log blocked generated text.
- Preserve English, Filipino, and Taglish support. Shared lexicon vocabulary is neutral; Taglish requires exclusive evidence from both languages.
- RAGService is the only retrieval component. Do not duplicate retrieval or bypass its threshold/ranking/source-attribution behavior.

## Notifications and frontend safety

- Notifications are persistent, recipient-scoped, in-app only, and explicitly marked read. A notification persistence failure must not roll back the authoritative appointment mutation.
- Do not add email, SMS, push, browser notifications, reminder scheduling, expiration, or deletion without approved scope.
- Reuse existing APIs and loaded authorized datasets rather than creating duplicate dashboard/search endpoints.
- Never interpolate untrusted dynamic values with `innerHTML`. Use DOM APIs and `textContent`; preserve privacy by excluding counselor notes and internal IDs from student-facing cards and calendar events.

## Security and privacy

- Do not log passwords, tokens, raw blocked AI output, private counselor notes, or protected conversation data.
- Treat all client input as untrusted, including request payloads and stored data rendered in the browser.
- Preserve ownership checks for students and assigned-staff checks for appointment lifecycle actions.
- Do not weaken fail-closed schedule/availability configuration handling.
- Do not expose ITSS administrators to guidance-specific data.

## Change discipline and verification

- Prefer extending existing routes, services, validators, and generic database helpers over adding parallel infrastructure.
- Use small private helpers only when they reduce genuine duplication. Do not introduce repositories, CQRS, event sourcing, ORM migrations, generic validation frameworks, base validators, new middleware, or global abstractions unless an approved issue explicitly requires one.
- Do not modify unrelated files. Do not stage, commit, push, or reset user work unless explicitly asked.
- Preserve an existing dirty worktree; inspect the diff and distinguish your changes from frozen/uncommitted work.

For every implementation, run at least:

```bash
python3 -m compileall backend/server
git diff --check
```

Run `node --check` for each affected frontend JavaScript file and focused tests for the changed rule. If dependencies prevent full application startup, state that limitation clearly and use isolated service checks where safe.
