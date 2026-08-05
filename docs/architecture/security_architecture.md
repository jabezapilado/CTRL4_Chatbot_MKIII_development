# CTRL4 Chatbot MK III — Security, Privacy, RBAC, and Sessions

> **Current reference.** This document describes implemented controls through
> Sprint 10. It does not turn future recommendations into current behavior.

## Implemented access boundaries

CTRL4 has exactly three canonical roles: `student`, `staff`, and `admin`.
Routes enforce authentication and role checks server-side; frontend access
checks are presentation only.

### Students

Students may use their own session/profile, chatbot, own appointments,
permitted cancellation/replacement rescheduling, own notifications, and the
approved generic case-status view. They must not receive counselor notes, case
notes, referrals, interventions, confidentiality records or reasons,
escalation reasons, conversation summaries, staff analytics, or internal
identifiers.

### Guidance staff

Guidance staff may use staff appointment, conversation, case-management,
settings, analytics, and reports workflows exposed by current staff route guards
and service authorization. Appointment visibility remains constrained by the
existing authorized-program/dynamic-routing model where that service applies.
Staff-wide flagged-case analytics are aggregate-only and do not imply personal
reviewer ownership.

### Administrators

Administrators manage accounts. They do not access guidance-specific records,
appointments, appointment lifecycle controls, conversations, flagged cases,
counselor notes, referrals, interventions, confidentiality records, or
analytics.

## Server-side session behavior

The application uses Flask-Session with CacheLib filesystem storage. The browser
receives only an opaque `ctrl4_session` identifier and normal cookie metadata;
authenticated-user data and escalation markers remain server-side.

- `HttpOnly` is enabled.
- `SameSite=Lax` is enabled.
- `Secure` is configurable and required in production.
- Permanent sessions expire after eight hours.
- Login clears and rotates/replaces the session identifier to prevent session
  fixation; logout clears and invalidates the session.
- The currently supported deployment is one application instance. Horizontal
  scaling requires an approved shared server-side session backend first.

## Data and conversation privacy

Services own privacy projection. Raw chat transcript/history is temporary and
is not permanently stored; `conversation_summaries.transcript_json` is not a
current persisted field. Finalized counselor summaries, approved metadata, and
case-management records are protected staff data. Student case status exposes
only approved generic fields.

Protected chat content—including raw messages, generated replies, prompts,
history, summaries, case data, and escalation reasons—is not logged. The
browser does not persist raw chat or escalation content in `localStorage` or
`sessionStorage`; obsolete protected keys are cleared when the chatbot starts.

## Browser safety and API behavior

Persisted and user-controlled dashboard values are rendered with DOM APIs and
`textContent`, not untrusted HTML interpolation. Endpoint-controlled JSON
responses use the established envelopes below. The pre-existing global 404/500
fallback remains a separate implementation detail with its current `error`
payload.

```json
{"success": true, "message": "...", "data": {}}
```

```json
{"success": false, "message": "...", "errors": null}
```

Services own business validation and privacy decisions; database helpers use
parameterized SQL and retain integrity protections such as constraints, enums,
transactions, and the atomic appointment conflict operation.

## AI safety

SafetyService handles pre-generation crisis/diagnosis safeguards in the detected
language and remains authoritative for escalation. ResponseSafetyService
performs deterministic post-generation checking and replaces an unsafe result
without logging blocked content. The chatbot does not provide medical or
psychological diagnosis, treatment, or prescription authority.

## Deferred security improvements

The following are documented future work, not implemented controls: CSRF
protection, restrictive production CORS policy, and a shared session store for
multi-instance deployment. Dependency modernization, including the
`google-generativeai` migration, is also deferred.
