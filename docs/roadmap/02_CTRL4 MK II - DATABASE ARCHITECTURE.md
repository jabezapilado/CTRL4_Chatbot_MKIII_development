# CTRL4 MK II - DATABASE ARCHITECTURE

> **Historical planning document.** Current frozen implementation references:
> [Project Context](../architecture/project_context.md) and
> [Project Architecture](../architecture/project_architecture.md).

> This document defines the database architecture of CTRL4 MK II.
>
> All database design decisions are considered LOCKED unless adviser requirements change.

---

# DATABASE DESIGN PHILOSOPHY

The database architecture follows the principles of:

- Data Minimization
- Privacy-by-Design
- Scalability
- Guidance Office Operational Requirements
- Role-Based Access Control
- Program-Based Counselor Assignment
- Temporary Conversation Persistence

The system shall only store information necessary for:

- Guidance Office operations
- Appointment management
- Student case management
- Counselor interventions
- Reports and analytics

---

# DATABASE TABLES

The core tables are:

1. accounts
2. appointments
3. inquiries
4. conversation_summaries
5. escalations
6. settings

No additional tables shall be created unless required by future adviser recommendations.

---

# ACCOUNTS TABLE

The accounts table manages:

- Students
- Guidance Counselors (Staff)
- ITSS Administrators

Fields:

```sql
id
email
password_hash
full_name

student_number
staff_number

gender

program

assigned_programs

office

support_statement

consultation_rooms

consultation_schedules

role

status

created_at
```

---

## STUDENT ACCOUNTS

Student-specific fields:

```text
student_number
program
```

Examples:

```text
2025-00001

BS Computer Science
```

---

## STAFF ACCOUNTS

Staff-specific fields:

```text
staff_number
assigned_programs
office
support_statement
consultation_rooms
consultation_schedules
```

Examples:

```json
assigned_programs

[
    "BS Computer Science",
    "BS Entertainment and Multimedia Computing"
]
```

```json
consultation_rooms

[
    "SJH-206",
    "PGN-105"
]
```

```json
consultation_schedules

[
    {
        "room":"SJH-206",
        "days":"Monday-Friday",
        "time":"7:00 AM - 5:00 PM"
    },

    {
        "room":"PGN-105",
        "days":"Monday-Friday",
        "time":"7:00 AM - 9:00 PM"
    }
]
```

---

## ADMIN ACCOUNTS

Admin accounts are responsible for:

- Account creation
- Account maintenance
- Access control

Admins SHALL NOT contain:

```text
assigned_programs
consultation_rooms
consultation_schedules
```

---

# VALID ACADEMIC PROGRAMS

The following academic programs are SYSTEM CONSTANTS.

```text
BS Computer Science

BS Cybersecurity

BS IT with specialization in Web Development

BS IT with specialization in Network Administration

BS Entertainment and Multimedia Computing
```

These values are NOT editable.

---

# APPOINTMENTS TABLE

The appointments table manages:

- Appointment requests
- Appointment history
- Appointment statuses
- Counselor notes
- Appointment sources

Final schema:

```sql
CREATE TABLE appointments (

id INT AUTO_INCREMENT PRIMARY KEY,

account_id INT NOT NULL,

contact_number VARCHAR(20) NOT NULL,

appointment_category VARCHAR(100) NOT NULL,

appointment_mode VARCHAR(50) NOT NULL,

preferred_date DATE NOT NULL,

preferred_time_slot VARCHAR(20) NOT NULL,

reason TEXT NOT NULL,

status ENUM(

'pending',
'approved',
'done',
'did_not_attend',
'cancelled'

) NOT NULL DEFAULT 'pending',

counselor_notes TEXT NULL,

appointment_source ENUM(
    'chatbot',
    'appointment_form',
    'walk_in',
    'hotline',
    'messenger',
    'email',
    'staff_manual'
    ) NOT NULL,

created_at DATETIME NOT NULL,

updated_at DATETIME NOT NULL,

FOREIGN KEY (account_id)
REFERENCES accounts(id)

);
```

---

# APPOINTMENT STATUS VALUES

The following values are LOCKED.

```text
Pending
Approved
Done
Did Not Attend
Cancelled
```

The following value SHALL NEVER exist:

```text
Rejected
```

---

# APPOINTMENT SOURCE VALUES

The following values are LOCKED.

```text
chatbot
appointment_form
walk_in
hotline
messenger
email
staff_manual
```

These are NOT editable.
The appointment source records only how an appointment request entered the system. It does not affect validation, conflict detection, counselor assignment, appointment status transitions, or other Appointment Engine business rules.

---

# APPOINTMENT HISTORY

Appointment history is stored directly in:

```text
appointments
```

No separate table is required.

Appointments SHALL NEVER be deleted unless required by institutional policies.

---

# PROGRAM-BASED APPOINTMENT ROUTING

Appointments are automatically routed using:

```text
Student Program
↓

Staff Assigned Programs
↓

Matching Counselor
```

Examples:

```text
BSCS

↓

Counselor A


--------------------------------


BSEMC

↓

Counselor A


--------------------------------


BSCYBER

↓

Counselor B
```

No manual assignment is required.

---

# SETTINGS TABLE

The settings table stores operational configurations.

Examples:

```text
office_information

appointment_categories

appointment_modes

consultation_schedules

office_days

chatbot_settings

faq_settings

knowledge_base_settings
```


JSON values may be used where appropriate.

The current implementation stores counselor-specific consultation schedules as JSON within the `accounts` table. Other operational configuration values (such as appointment categories, appointment modes, office information, and chatbot settings) are stored in the `settings` table as key-value records.

---

# APPOINTMENT SETTINGS DATA MODEL

The appointment settings module is composed of configurable operational data managed by Guidance Office staff.

## Guidance Rooms

Stores the consultation rooms available for appointments.

## Consultation Schedules

- Consultation schedules belong to guidance counselors.
- Each consultation schedule defines the assigned guidance room, office days, and available consultation time.
- Students select an available consultation schedule during appointment booking.
- Consultation schedules are currently stored as JSON within counselor accounts.

## Appointment Categories

Stores the configurable counseling categories.

## Appointment Modes

Stores the configurable appointment modes.

## Office Days

Stores the operating days during which appointments may be accepted.

## Relationships

```text
Office Days
        ↓
Guidance Rooms
        ↓
Consultation Schedules
        ↓
Appointments
```

## Design Rules

- Students select an available consultation schedule during booking.
- The assigned guidance room is derived automatically from the selected consultation schedule.
- Consultation schedules belong to guidance counselors.
- Multiple counselors may use the same guidance room when their consultation schedules permit.
- Duplicate guidance room names are not allowed.
- Configuration records referenced by appointments should be deactivated (soft delete) instead of permanently deleted.

---

# CONVERSATION SUMMARIES TABLE

The conversation_summaries table stores:

- AI Counselor Intake Summaries
- Emotion Detection Results
- Recommendations
- Conversation Metadata

The table SHALL NOT store:

Active conversations are maintained only as temporary session data during an authenticated user session. Temporary conversation data is used solely to preserve conversational context and is automatically deleted after AI Counselor Intake Summary generation. Only the generated summary and related metadata are permanently stored in the database.

- Raw conversations
- Chat logs
- Message history

Examples:

```text
Primary Concern

Conversation Type

Emotion Results

Flagged Status

Recommendations

Appointment Recommendation

Language Used

Total Messages

Summary

Created At
```

---

# INQUIRIES TABLE

The inquiries table stores:

- Inquiry metadata
- Inquiry categories
- Emotion detection results
- Escalation status

This table supports:

- General inquiries
- Guidance-related inquiries
- Appointment inquiries

---

# ESCALATIONS TABLE

The escalations table stores:

- Escalated student concerns
- Flagged intervention records
- Counselor reviews

Escalations are generated when:

- Negative emotion is detected.
- Counselor intervention is required.
- Manual escalation is necessary.

---

# ROLE-BASED ACCESS CONTROL

Students may access:

- Their own appointments
- Their own appointment statuses

Staff may access:

- Appointment records
- Flagged cases
- Counselor notes
- Reports
- Settings

Admins may access:

- Accounts
- System access management

Admins SHALL NOT access:

- Counselor notes
- Appointment management
- Guidance Office operational settings

---

# DATA RETENTION POLICY

The system SHALL permanently retain:

- Appointment records
- Counselor notes
- AI summaries
- Conversation metadata
- Reports
- Settings

The system SHALL NOT permanently retain:

- Raw conversations
- Chat logs
- Conversation exports

---

# DATABASE DESIGN DECISIONS

The following decisions are FINAL:

- Program-based counselor assignment.
- No guest appointments.
- Appointment history uses the appointments table.
- Appointment statuses are system constants.
- Appointment sources are system constants.
- Academic programs are system constants.
- Staff consultation schedules are currently stored as JSON within counselor accounts.
- Operational system configuration is stored in the settings table using key-value records.
- Raw conversations are never stored in the database.
- AI summaries are permanently stored.
- Appointment records are permanently stored.
- Data minimization principles are enforced.
- Active conversations are never stored permanently in the database.
- Temporary conversation persistence exists only for authenticated session continuity.
- Only AI Counselor Intake Summaries and conversation metadata are retained after conversation finalization.
- Appointment Form and AI Guidance Chatbot share the same Appointment Engine and appointment records.
