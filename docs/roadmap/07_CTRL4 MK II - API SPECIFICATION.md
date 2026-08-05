# CTRL4 MK II - API SPECIFICATION

> **Historical planning document.** Current frozen implementation references:
> [PROJECT_CONTEXT.md](../PROJECT_CONTEXT.md) and
> [01_project_architecture.md](../01_project_architecture.md).

> This document defines the official REST API contract of CTRL4 MK II.
>
> It serves as the communication contract between the frontend and backend. All API implementations shall conform to this specification unless adviser requirements change.

---

# API DESIGN PRINCIPLES

The CTRL4 MK II API follows RESTful design principles.

- JSON request and response bodies
- UTF-8 encoding
- JWT Authentication
- ISO 8601 date and time format
- Consistent response structure
- Consistent HTTP status codes

---

# BASE URL

```text
/api
```

---

# AUTHENTICATION

Protected endpoints require:

```http
Authorization: Bearer <JWT>
```

---

# STANDARD RESPONSE FORMAT

## Successful Response

```json
{
    "success": true,
    "message": "Request completed successfully.",
    "data": {}
}
```

## Error Response

```json
{
    "success": false,
    "message": "Validation failed.",
    "errors": {}
}
```

---

# AUTHENTICATION MODULE

## POST /api/auth/login

Authenticate a user.

### Request

```json
{
    "email": "",
    "password": ""
}
```

### Response

```json
{
    "token": "",
    "account": {}
}
```

---

## POST /api/auth/logout

Logout the current user.

---

## GET /api/auth/me

Return the authenticated account.

---

# STUDENT APPOINTMENTS

## POST /api/appointments

Create a new appointment request.

### Request

```json
{
    "appointment_category": "",
    "appointment_mode": "",
    "preferred_date": "",
    "preferred_time_slot": "",
    "contact_number": "",
    "reason": ""
}
```

### Response

```json
{
    "appointment_id": 1,
    "status": "pending"
}
```

---

## GET /api/appointments

Return the student's appointment history.

---

## GET /api/appointments/{id}

Return appointment details.

---

## PATCH /api/appointments/{id}/cancel

Cancel an appointment.

---

## POST /api/appointments/{id}/reschedule

Reschedule an appointment.

---

# STAFF APPOINTMENTS

## GET /api/staff/appointments

Return all appointments.

---

## POST /api/appointments/manual

Create a manual appointment.

---

## PATCH /api/appointments/{id}/approve

Approve an appointment.

---

## PATCH /api/appointments/{id}/done

Mark an appointment as completed.

---

## PATCH /api/appointments/{id}/did-not-attend

Mark an appointment as Did Not Attend.

---

## PATCH /api/appointments/{id}/cancel

Cancel an appointment.

---

# CHATBOT

The Chatbot API manages conversational interactions only. Appointment creation, validation, conflict detection, and counselor assignment are delegated to the shared Appointment Engine through the Appointment Service.

## POST /api/chatbot/message

Send a chatbot message.

### Request

```json
{
    "message": ""
}
```

### Response

```json
{
    "reply": "",
    "appointment_recommended": false,
    "appointment_detected": false,
    "flagged": false
}
```

---

## GET /api/chatbot/session

Return the active conversation session for the authenticated user.

The endpoint restores the active conversation while the authenticated session remains valid. It does not return permanently stored conversation history.

---

## POST /api/chatbot/session/finalize

Finalize the active conversation.

This endpoint generates the AI Counselor Intake Summary, stores the approved summary and metadata, and permanently deletes the temporary conversation data. It is intended for logout and automatic session timeout workflows rather than direct user interaction.

---

# CONVERSATION SUMMARIES

## GET /api/conversation-summaries

Return counselor intake summaries.

---

## GET /api/conversation-summaries/{id}

Return a single AI Counselor Intake Summary.

---

# FLAGGED CASES

## GET /api/flagged-cases

Return flagged student cases.

---

## PATCH /api/flagged-cases/{id}/resolve

Resolve a flagged case.

---

# STUDENT CASE MANAGEMENT

## GET /api/cases

Return student cases.

---

## GET /api/cases/{id}

Return a case record.

---

## POST /api/cases/{id}/notes

Create counselor notes.

---

# GUIDANCE OFFICE SETTINGS

## GET /api/settings

Retrieve operational settings.

---

## PATCH /api/settings

Update operational settings.

---

# COUNSELOR SETTINGS

## GET /api/counselors

Return counselor information.

---

## PATCH /api/counselors/{id}

Update counselor configuration.

---

# REPORTS

## GET /api/reports/dashboard

Dashboard statistics.

---

## GET /api/reports/appointments

Appointment analytics.

---

## GET /api/reports/flagged-cases

Flagged case analytics.

---

# ACCOUNT MANAGEMENT

## GET /api/accounts

List accounts.

---

## POST /api/accounts

Create an account.

---

## PATCH /api/accounts/{id}

Update an account.

---

## DELETE /api/accounts/{id}

Deactivate an account.

---

# HTTP STATUS CODES

| Code | Description |
|------|-------------|
|200|Success|
|201|Created|
|204|No Content|
|400|Bad Request|
|401|Unauthorized|
|403|Forbidden|
|404|Not Found|
|409|Conflict|
|422|Validation Error|
|500|Internal Server Error|

---

# API VERSION

Current Version

```text
v1
```

---

# DESIGN PRINCIPLES

The API SHALL:

- Follow RESTful conventions.
- Return JSON responses.
- Validate all incoming requests.
- Enforce Role-Based Access Control.
- Follow the Appointment Engine business rules.
- Follow the Data Privacy architecture.
- Maintain backward compatibility within the same API version.
- Chatbot conversation management is independent of appointment business logic.
- The Appointment Engine serves both the AI Guidance Chatbot and the Appointment Form.
- Temporary conversation sessions are restored only while the authenticated session remains valid.
- Raw conversation data is temporary and is deleted after AI Counselor Intake Summary generation.

---

# LOCKED DESIGN DECISIONS

The following API decisions are FINAL:

- JWT Authentication is required for protected endpoints.
- JSON is the only supported request and response format.
- All responses use a consistent response envelope.
- Business logic resides in the Service Layer.
- Validation occurs before database operations.
- API routes remain thin and delegate business logic to services.
- Version 1 endpoints use the `/api` base path.
- The Chatbot API never implements appointment business rules directly.
- Conversation restoration is limited to the active authenticated session.
- Appointment submission does not terminate the active conversation.
- AI Counselor Intake Summaries are generated before temporary conversation data is deleted.
- The API does not expose permanent raw conversation history.
