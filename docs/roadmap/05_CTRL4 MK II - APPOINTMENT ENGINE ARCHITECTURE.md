

# CTRL4 MK II - APPOINTMENT ENGINE ARCHITECTURE

> This document defines the appointment business logic architecture of CTRL4 MK II.
>
> All Appointment Engine decisions are considered **LOCKED** unless adviser requirements change.

---

# PURPOSE

The Appointment Engine manages the complete appointment lifecycle from booking to completion.

Its responsibilities are to:

- Validate appointment requests.
- Perform appointment conflict detection.
- Automatically assign counselors using program-based routing.
- Create appointment records.
- Manage appointment status transitions.
- Support chatbot and manual appointment creation.
- Provide a single source of truth for appointment business logic.

---

# APPOINTMENT LIFECYCLE

## Student Appointment

```text
Student
    ↓
Submit Appointment Request
    ↓
Validation
    ↓
Conflict Detection
    ↓
Program-Based Counselor Assignment
    ↓
Save Appointment
    ↓
Pending
```

## Manual Appointment

```text
Guidance Staff
    ↓
Search Student
    ↓
Validation
    ↓
Conflict Detection
    ↓
Program-Based Counselor Assignment
    ↓
Save Appointment
    ↓
Approved
```

---

# APPOINTMENT STATUS WORKFLOW

```text
Pending
    ├── Approved
    │      ├── Done
    │      ├── Did Not Attend
    │      └── Cancelled
    └── Cancelled
```

Only the transitions shown above are permitted.

---

# VALIDATION PIPELINE

Every appointment request follows the same validation sequence.

```text
Student Exists
        ↓
Student Active
        ↓
Contact Number Provided
        ↓
Valid Appointment Date
        ↓
Date Not In The Past
        ↓
Office Accepts Appointments
        ↓
Valid Consultation Schedule
        ↓
Conflict Detection
        ↓
Program-Based Counselor Assignment
        ↓
Save Appointment
```

Validation stops immediately when any rule fails.

---

# CONFLICT DETECTION

Version 1 determines conflicts using:

- Preferred Date
- Preferred Time Slot
- Appointment Status = Pending or Approved

This reflects the current database implementation.

---

# PROGRAM-BASED COUNSELOR ASSIGNMENT

```text
Student Program
        ↓
Assigned Programs
        ↓
First Matching Counselor
```

Students never select a counselor directly.

---

# APPOINTMENT SOURCES

Supported appointment sources:

- Chatbot
- Walk-in
- Hotline
- Messenger
- Email
- Staff Manual

These values are treated as system constants.

---

# APPOINTMENT CREATION RULES

Student appointments:

- Initial Status: Pending

Manual appointments:

- Initial Status: Approved

Automatically generated values:

- created_at
- updated_at

---

# API CONTRACT

## Student APIs

- POST `/api/appointments`
- GET `/api/appointments`
- GET `/api/appointments/{id}`
- PATCH `/api/appointments/{id}/cancel`

## Staff APIs

- POST `/api/appointments/manual`
- PATCH `/api/appointments/{id}/approve`
- PATCH `/api/appointments/{id}/done`
- PATCH `/api/appointments/{id}/did-not-attend`
- PATCH `/api/appointments/{id}/cancel`

---

# DESIGN PRINCIPLES

The Appointment Engine follows these principles:

- Single source of truth for appointment business logic.
- Consistent validation regardless of appointment source.
- Automatic program-based counselor assignment.
- Centralized conflict detection.
- Predictable appointment status transitions.
- Separation of business logic from database access.