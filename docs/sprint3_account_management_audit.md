# Sprint 3 Account Management Audit

Status: Verified for GitHub Issue #26

This audit records the final account-management review for Sprint 3. It treats
Issues #19 through #25 as frozen and verifies the completed account module
without changing runtime behavior.

## Scope

Issue #26 requires a final review verifying that:

- Student accounts function correctly.
- Staff accounts function correctly.
- Administrator accounts function correctly.
- Program assignments work properly.
- Validation rules are enforced.
- API responses are consistent.

This audit covers the account and authentication surfaces only:

- `backend/server/routes/account_routes.py`
- `backend/server/services/account_service.py`
- `backend/server/db.py`
- `backend/server/auth.py`
- `backend/server/request_validation.py`
- `frontend/templates/login.html`

## Architecture Verification

The account module preserves the project layering:

- Routes own HTTP request parsing, RBAC checks, logging, status codes, and
  response envelopes.
- Services own business validation, account role rules, duplicate email
  translation, password verification, and account-management decisions.
- Database helpers own persistence, SQL parameterization, account-number
  generation, role/status normalization, and defensive integrity safeguards.

Authentication remains Flask server-side session based. The service layer does
not own Flask session state.

## Account Functionality

Student account management is implemented through the shared account creation
flow, student-specific update/deactivation services, and the administrative
account listing. Student updates accept only the approved student profile
fields: `full_name`, `email`, `gender`, and `program`.

Staff account management reuses the shared creation and listing flow while
keeping staff profile validation separate. Staff profile metadata includes
`assigned_programs`, `office`, `support_statement`, `consultation_rooms`, and
`consultation_schedules`. Consultation data is stored as profile metadata only.

Administrator account management reuses the shared creation, listing, fetch,
and update database primitives. Administrator updates accept only
`full_name`, `email`, and `gender`. Administrator creation rejects unsupported
student, staff, counselor, and account-number fields. Administrators cannot
deactivate their own account.

## Program Assignments

Student program validation uses the configured program list. Staff assigned
programs use the same configured program source and reject invalid, blank, or
duplicate program values.

Appointment routing remains dynamic and program based. Staff assignment is
resolved from the current `assigned_programs` profile metadata. Appointments do
not persist counselor ownership.

## Validation

Business validation is centralized in `account_service.py`:

- Full name, email, gender, role, status, and student program validation use
  shared service helpers.
- Student, staff, and administrator update flows reject unsupported fields.
- Duplicate email pre-checks are performed in the service layer.
- Persistence-level duplicate email collisions are translated back to the
  existing duplicate-email service error.

The database layer retains defensive integrity safeguards:

- Unique constraints for email, student number, and staff number.
- Allowed account roles and statuses.
- Automatic student and staff number generation.
- Role-based cleanup of fields that must not persist for a given account type.

## API Responses

Account and authentication responses use the established envelope:

- Success responses include `success`, `message`, and `data`.
- Error responses include `success`, `message`, and `errors: null`.
- Login now returns the authenticated user inside `data`.
- RBAC errors from request validation use the same error envelope.

Existing HTTP status behavior is preserved:

- `200` for successful retrieval, update, deactivation, login, and logout.
- `201` for successful account creation.
- `400` for validation errors.
- `401` for unauthenticated or invalid login attempts.
- `403` for forbidden role access.
- `404` for missing role-specific account targets.
- `409` for duplicate email conflicts.

## Result

The current implementation satisfies GitHub Issue #26. No runtime code changes
are required for the final account-management audit beyond this documentation
record.
