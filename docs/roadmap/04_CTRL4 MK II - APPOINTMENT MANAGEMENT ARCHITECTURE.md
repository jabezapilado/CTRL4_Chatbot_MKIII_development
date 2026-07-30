# CTRL4 MK II - APPOINTMENT MANAGEMENT ARCHITECTURE

> This document defines the appointment management architecture, counselor assignment logic, dashboard design, appointment workflows, and staff configuration settings of CTRL4 MK II.

---

# DESIGN PHILOSOPHY

The Appointment Management Module was designed to support the operational workflow of the Guidance Office.

The module supports:

- Student appointment requests
- Counselor interventions
- Manual appointment creation
- Program-based counselor assignment
- Appointment monitoring
- Appointment history
- Appointment analytics
- Counselor notes
- Guidance Office appointment settings

The appointment module is NOT a standalone appointment system.

It is a component of the Guidance Office Management System.

The Appointment Management Module is shared by both the traditional appointment form and the AI Guidance Chatbot. Both interfaces use the same appointment management workflow, business rules, validation, counselor assignment, and conflict detection logic.

---

# APPOINTMENT MANAGEMENT MODULE

Features:

- Appointment Booking
- Shared Appointment Management
- Chatbot and Appointment Form Integration
- Appointment Conflict Detection
- Appointment Monitoring
- Appointment History
- Appointment Analytics
- Manual Appointment Entry
- Program-Based Counselor Assignment
- Counselor Notes
- Appointment Settings
- Staff Dashboard Monitoring

---

# APPOINTMENT SOURCES

Students may create appointments through:

- AI Guidance Chatbot
- Appointment Form

Staff users may create appointments through:

- Walk-in
- Hotline
- Messenger
- Email
- Staff Manual Entry

The following values are SYSTEM CONSTANTS:

```text
chatbot
appointment_form
walk_in
hotline
messenger
email
staff_manual
```

These values are NOT editable.

---

# STUDENT APPOINTMENT BOOKING

Students may choose either booking method:

- AI Guidance Chatbot
- Appointment Form

Both methods use the same appointment management workflow, validation rules, conflict detection, counselor assignment, and appointment statuses.

Students may switch between the chatbot and the appointment form without losing the active conversation while the authenticated session remains active.

---

# APPOINTMENT WORKFLOWS

## CHATBOT APPOINTMENTS

```
Student

↓

Book Appointment

↓

Choose Booking Method

↓

Chatbot
OR
Appointment Form

↓

Submit Request

↓

Pending

↓

Staff Review

↓

Approved

↓

Done

OR

Did Not Attend

OR

Cancelled
```

Submitting an appointment request does not terminate the active conversation. Students may continue interacting with the chatbot after the appointment has been successfully submitted.

Only chatbot appointments begin with:

```text
Pending
```

---

## MANUAL APPOINTMENTS

```
Walk-in

OR

Hotline

OR

Messenger

OR

Email

↓

Staff Manual Entry

↓

Automatically Approved

↓

Done

OR

Did Not Attend

OR

Cancelled
```

Manual appointments SHALL NOT become Pending.

---

# APPOINTMENT STATUSES

The following appointment statuses are LOCKED.

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

# APPOINTMENT STATUS WORKFLOW

## Pending

Available actions:

- Approve
- Cancel

---

## Approved

Available actions:

- Done
- Did Not Attend
- Cancelled

---

## Done

Available actions:

- View Counselor Notes

---

## Did Not Attend

Available actions:

- View Appointment Details

---

## Cancelled

Available actions:

- View Appointment Details

---

# APPOINTMENT CONFLICT DETECTION

Before an appointment is created, the system shall validate:

```text
Preferred Date

+

Preferred Time Slot
```

The system checks whether an existing appointment already has:

```text
Pending

OR

Approved
```

If TRUE:

```text
This schedule is already taken.
```

The appointment SHALL NOT be created.

This applies to:

- Chatbot appointments
- Walk-in appointments
- Hotline appointments
- Messenger appointments
- Email appointments
- Manual staff appointments

NO EXCEPTIONS.

---

# PROGRAM-BASED COUNSELOR ASSIGNMENT

Appointments are automatically routed based on:

```text
Student Program

↓

Assigned Programs

↓

Matching Counselor

↓

Appointment Dashboard
```

Examples:

```text
BS Computer Science

↓

Sir Ryan


--------------------------------


BS Entertainment and Multimedia Computing

↓

Sir Ryan


--------------------------------


BS Cybersecurity

↓

Ma'am Hannah


--------------------------------


BS IT - Web Development

↓

Ma'am Hannah


--------------------------------


BS IT - Network Administration

↓

Ma'am Hannah
```

No manual counselor assignment is required.

---

# VALID ACADEMIC PROGRAMS

The following programs are SYSTEM CONSTANTS.

```text
BS Computer Science

BS Cybersecurity

BS IT with specialization in Web Development

BS IT with specialization in Network Administration

BS Entertainment and Multimedia Computing
```

These values are NOT editable.

---

# APPOINTMENT FORM

Students SHALL ONLY provide:

- Contact Number
- Appointment Category
- Appointment Mode
- Preferred Date
- Preferred Time Slot
- Reason

The system automatically retrieves:

- Student Name
- Student Number
- Program
- Email Address

through the authenticated account.

---

# APPOINTMENT MODIFICATION POLICY

Students MAY:

- View their own appointments.
- Cancel their own appointments.
- Reschedule their own appointments.

Students SHALL NOT:

- Cancel appointments that are scheduled within the next 1 hour.
- Reschedule appointments that are scheduled within the next 1 hour.

If the appointment is less than 1 hour away, the system shall display:

This appointment can no longer be modified because it is scheduled within the next hour.

The 1-hour restriction shall be enforced by:

- Frontend validation
- Backend route validation
- Appointment management business logic

The restriction SHALL NOT rely solely on the user interface.

Staff users MAY:

- Cancel appointments at any time.
- Reschedule appointments at any time.
- Modify appointment statuses at any time.

The 1-hour appointment modification restriction applies ONLY to student users.

## DIRECT APPOINTMENT EDITING

Direct appointment editing is NOT supported.

Students SHALL NOT modify:

- Preferred Date
- Preferred Time Slot
- Appointment Category
- Appointment Mode
- Reason

The appointment modification workflow is:

Student Appointment
↓

Modify Appointment?

↓

Cancel
OR
Reschedule

---------------------------------

Cancel

↓

Is appointment within 1 hour?

↓

YES

Display restriction message.

↓

NO

Appointment becomes Cancelled.


---------------------------------

Reschedule

↓

Is appointment within 1 hour?

↓

YES

Display restriction message.

↓

NO

Current appointment becomes Cancelled.

↓

Student creates a new appointment request.

↓

Appointment Conflict Detection.

↓

Pending.

↓

Staff Review.

---

# APPOINTMENT DETAILS

Staff users should be able to view:

```text
Student Name

Student Number

Program

Email Address

Contact Number

Appointment Category

Appointment Mode

Preferred Date

Preferred Time Slot

Reason

Appointment Source

Status

Counselor Notes
```

---

# MANUAL APPOINTMENT ENTRY

Staff users may create appointments for:

- Walk-in
- Hotline
- Messenger
- Email

Required fields:

```text
Student Name

Student Number

Appointment Category

Appointment Mode

Preferred Date

Preferred Time Slot

Reason

Appointment Source
```

Manual appointments are automatically:

```text
Approved
```

Guest appointments are NOT supported.

Students MUST have existing accounts.

---

# COUNSELOR NOTES

Counselor Notes are only editable by Staff users.

Examples:

```text
Student was advised regarding academic concerns.

----------------------------------

Follow-up counseling session recommended.

----------------------------------

Student referred for further evaluation.

----------------------------------

Student requested additional counseling support.
```

---

# COUNSELOR NOTES REQUIREMENTS

Optional:

```text
Approved

Did Not Attend

Cancelled
```

NOT ALLOWED:
```text
Pending
```

Required:

```text
Done
```

Counselor Notes form part of the student's appointment history.

---

# APPOINTMENT HISTORY

Appointments SHALL serve as the student's:

```text
Appointment History
```

No separate table is required.

Appointment records SHALL NOT be deleted unless institutional policies require deletion.

Appointment history includes:

- Appointment Information
- Appointment Status
- Counselor Notes
- Appointment Source
- Appointment Dates
- Appointment Category

---

# STAFF APPOINTMENT DASHBOARD

The previous slot management system SHALL be removed.

REMOVE:

```text
Total Slots

Available Slots

Reserved Slots

Appointment Availability

Add Availability Slot

Mark Available
```

These features no longer align with the thesis scope.

---

# NEW STAFF APPOINTMENT DASHBOARD

Dashboard Cards:

```text
Total Appointments Today

Pending Requests

Completed Today
```

---

## Dashboard Sections

```text
Appointment Requests

---------------------------------

Today's Appointments

---------------------------------

Appointment History

---------------------------------

Flagged Cases Requiring Appointment

---------------------------------

Manual Appointment Entry
```

---

# APPOINTMENT SETTINGS

Appointment Settings are editable ONLY by Staff users.

## Design Philosophy

Appointment schedules are manually configured by staff to provide maximum flexibility and accurately reflect the Guidance Office's daily operations.

## Appointment Settings Architecture

Appointment Settings is composed of five configurable modules.

```text
Appointment Settings
│
├── Available Days
├── Guidance Rooms
├── Time Slots
├── Appointment Modes
└── Appointment Categories
```

These configuration modules are database-driven and are managed exclusively by Staff users.

All appointment booking—whether initiated by students or staff—uses these shared configuration records.

## Available Days

Staff may configure the days on which appointments are accepted.

## Guidance Rooms

Staff may:

- Add guidance rooms.
- Edit guidance rooms.
- Deactivate guidance rooms.
- Manage room availability for future appointments.

## Time Slots

- Time slots are manually created by staff.
- Every time slot belongs to exactly one guidance room.
- Students select only the available time slot.
- The corresponding room is automatically determined from the selected time slot.

## Appointment Modes

Configurable by staff.

## Appointment Categories

Configurable by staff.

## Configuration Dependencies

```text
Available Days
        ↓
Guidance Rooms
        ↓
Time Slots
        ↓
Student & Manual Appointments
```

The configuration modules work together as follows:

- Available Days determine when appointments may be scheduled.
- Guidance Rooms provide the locations assigned to time slots.
- Time Slots define the schedules available for booking.
- Appointment Modes and Appointment Categories are selected during appointment creation.
- Both student appointments and manual appointments use the same configuration records.

## Student Booking Flow

```text
Student

↓

Select Date

↓

Load Available Time Slots

↓

Select Time Slot

↓

Submit Appointment
```

## Manual Appointment Flow

```text
Staff

↓

Search Existing Student

↓

Create Appointment

↓

Automatically Approved
```

## Conflict Detection

All appointment sources use the same appointment conflict detection rules.

## Validation Rules

- Duplicate guidance room names are not allowed.
- Duplicate time slots for the same room are not allowed.
- End time must be later than the start time.
- Guidance rooms referenced by time slots should be deactivated instead of permanently deleted.

## Locked Design Decisions

- Students never select guidance rooms directly.
- Guidance rooms are derived automatically from the selected time slot.
- Staff-defined time slots are the only valid appointment schedules.
- Student appointments and manual appointments use the same time slot configuration and conflict detection logic.

---

# GUIDANCE COUNSELOR SETTINGS

Editable by Staff users.

Fields include:

```text
Assigned Programs

Office Assignment

Support Statement

Consultation Rooms

Consultation Schedules
```

Examples:

```text
Assigned Programs:

- BS Computer Science
- BS Entertainment and Multimedia Computing

----------------------------------

Office:

University Guidance Center

----------------------------------

Support Statement:

Counseling services are available both online and onsite.

----------------------------------

Consultation Rooms:

- SJH-206
- PGN-105

----------------------------------

Consultation Schedule:

Monday to Friday

7:00 AM - 5:00 PM

Monday to Friday

7:00 AM - 9:00 PM
```

---

# GUIDANCE OFFICE SETTINGS

Editable by Staff users.

Fields include:

```text
Office Name

Office Hours

Office Email

Office Contact Number

Office Location
```

Examples:

```text
University Guidance Center

Monday to Friday

7:00 AM - 5:00 PM

guidance@hau.edu.ph

Holy Angel University
```

---

# APPOINTMENT ANALYTICS

The system shall generate:

## Appointment Statistics

```text
Total Appointments

Pending

Approved

Completed

Cancelled

Did Not Attend
```

---

## Appointment Source Statistics

Examples:

```text
Chatbot - 20

Walk-in - 5

Messenger - 3

Hotline - 2

Email - 1
```

---

## Appointment Category Statistics

Examples:

```text
Career / Schooling - 12

Personality Development - 8

Relationships - 6

Health and Recreation - 4
```

---

## Program Statistics

Examples:

```text
BSCS - 15

BSCYBER - 10

BSIT-WD - 8

BSIT-NA - 6

BSEMC - 4
```

---

## Counselor Statistics

Examples:

```text
Sir Ryan - 20

Ma'am Hannah - 23
```

---

# STUDENT CASE MANAGEMENT INTEGRATION

Appointments are directly integrated with:

- AI Counselor Intake Summaries
- Flagged Cases
- Counselor Notes
- Reports and Analytics
- Resolved Cases

Examples:

```text
Student Conversation

↓

Flagged Case

↓

Appointment Request

↓

Counselor Intervention

↓

Appointment Completed

↓

Resolved Student Case
```

Appointments are one component of the student's overall case history.

---

# LOCKED DESIGN DECISIONS

The following decisions are FINAL:

- Program-based counselor assignment.
- Manual appointment support.
- Appointment conflict detection for all sources.
- Manual appointments automatically become Approved.
- Appointment statuses are system constants.
- Appointment sources are system constants.
- Academic programs are system constants.
- Staff manages appointment settings.
- No slot management system.
- No Rejected appointment status.
- Appointment history uses the appointments table.
- Counselor Notes are part of appointment history.
- Guest appointments are not supported.
- Appointments are integrated with Student Case Management.
- Students may cancel or reschedule their own appointments.
- Students cannot cancel or reschedule appointments that are scheduled within the next 1 hour.
- The 1-hour appointment modification restriction applies only to students.
- Staff users may manage appointments regardless of the remaining time before the scheduled appointment.
- Students SHALL NEVER directly edit appointment information.
- Rescheduling is implemented by cancelling the current appointment and creating a new appointment request.
- Direct appointment editing is not supported.
- Students may book appointments through either the AI Guidance Chatbot or the Appointment Form.
- Both booking methods use the same appointment management workflow and business rules.
- Appointment submission does not terminate an active conversation.
- Students may return to the chatbot after using the appointment form while preserving the active conversation.
