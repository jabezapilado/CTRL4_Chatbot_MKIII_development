# CTRL4 MK II - MASTER DEVELOPMENT ROADMAP

> Thesis Title:
>
> Development of an AI-Powered Chatbot for Inquiry Management Using NLP-Based Negative Emotion Detection
>
> System Name:
>
> CTRL4 MK II

---

# SYSTEM OVERVIEW

CTRL4 MK II is NOT merely an AI chatbot.

CTRL4 MK II is an:

> AI-Powered Guidance Office Management System with an Integrated Guidance Chatbot for Inquiry Management, NLP-Based Negative Emotion Detection, Appointment Management, Student Case Management, and Guidance Counselor Support Services.

The chatbot is only one component of the entire system.

The system was designed to support the operational needs of the Guidance Office while providing students with an intelligent and privacy-preserving counseling support platform.

---

# SYSTEM MODULES

## AI Chatbot Module

Features:

- Guidance-related inquiries
- Knowledge Base (RAG)
- FAQs
- Academic Support
- Guidance Services
- Appointment Booking Interface
- Office Information
- Real-time NLP Processing

---

## Conversation Management Module

Features:

- Temporary Conversation Processing
- Automatic Conversation Management
- AI Counselor Intake Summary Generation
- Topic Classification
- Conversation Statistics
- Session Management

---

## Appointment Management Module

Features:

- Appointment Booking
- Appointment Conflict Detection
- Appointment Monitoring
- Appointment History
- Appointment Analytics
- Manual Appointment Entry
- Appointment Settings
- Appointment Routing

---

## Student Case Management Module

Features:

- Conversation Summaries
- Flagged Cases
- Counselor Interventions
- Appointment Records
- Recommendations
- Resolved Cases

---

## Guidance Office Management Module

Features:

- Guidance Office Information
- Appointment Management
- Settings Management
- Counselor Management
- Flagged Case Monitoring
- Reports and Analytics

---

## Guidance Counselor Support Module

Features:

- Counselor Notes
- Appointment Records
- Follow-up Recommendations
- Student Case Monitoring
- Manual Interventions

---

## Account Management Module

Features:

- Student Accounts
- Staff Accounts
- System Access Management
- Role Management

---

# USER ROLES

## STUDENTS

Capabilities:

- Use the AI Chatbot
- Ask Guidance-related questions
- Book appointments
- View appointment details
- Receive appointment updates

Students cannot:

- Access staff information
- Access appointment records of other students
- View flagged cases
- View counselor notes

---

## STAFF (GUIDANCE COUNSELORS)

Capabilities:

- Manage appointments
- Monitor appointments
- Review flagged cases
- Add counselor notes
- Manage Guidance Office settings
- Manage appointment settings
- Create manual appointments
- View reports and analytics
- Manage counselor information

Staff users are responsible for Guidance Office operations.

---

## ADMIN (ITSS)

Capabilities:

- Create student accounts
- Create staff accounts
- Edit accounts
- Disable accounts
- Manage system access

Admins are NOT Guidance Counselors.

Admins SHALL NOT:

- Manage appointments
- Manage counselor notes
- Manage appointment settings
- Manage Guidance Office configurations

Admins are responsible only for system administration.

---

# VALID ACADEMIC PROGRAMS

The following programs are system constants:

- BS Computer Science
- BS Cybersecurity
- BS IT with specialization in Web Development
- BS IT with specialization in Network Administration
- BS Entertainment and Multimedia Computing

These values are NOT editable.

---

# PROGRAM-BASED COUNSELOR ASSIGNMENT

Appointments are automatically routed based on the student's academic program.

Students have:

- Program

Staff users have:

- Assigned Programs

Examples:

- BSCS → Counselor A
- BSEMC → Counselor A
- BSCYBER → Counselor B
- BSIT-WD → Counselor B
- BSIT-NA → Counselor B

The appointment routing process is fully automatic.

No manual counselor assignment is required.

---

# APPOINTMENT MANAGEMENT SYSTEM

## Appointment Sources

Student-created:

- Chatbot

Staff-created:

- Walk-in
- Hotline
- Messenger
- Email
- Staff Manual Entry

All appointment sources MUST use the same conflict detection algorithm.

---

# APPOINTMENT WORKFLOW

## Chatbot Appointment Workflow

Student
↓
Book Appointment
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

---

## Manual Appointment Workflow

Walk-in
OR
Messenger
OR
Hotline
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

---

# APPOINTMENT STATUSES

The following statuses are system constants:

- Pending
- Approved
- Done
- Did Not Attend
- Cancelled

The following status SHALL NOT exist:

- Rejected

---

# APPOINTMENT FORM

Students are only required to provide:

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

- Directly edit appointment information.
- Cancel appointments that are scheduled within the next 1 hour.
- Reschedule appointments that are scheduled within the next 1 hour.

If the appointment is less than 1 hour away, the system shall display:

> This appointment can no longer be modified because it is scheduled within the next hour.

The 1-hour restriction shall be enforced by:

- Frontend validation
- Backend route validation
- Appointment management business logic

The restriction SHALL NOT rely solely on the user interface.

This restriction applies regardless of:

- Appointment Category
- Appointment Mode
- Appointment Source

Staff users MAY:

- Cancel appointments at any time.
- Reschedule appointments at any time.
- Modify appointment statuses at any time.

The 1-hour appointment modification restriction applies ONLY to student users.

DIRECT APPOINTMENT EDITING

Students SHALL NOT:

- Directly edit appointment information.
- Change appointment statuses.
- Mark appointments as Done.
- Mark appointments as Cancelled.
- Mark appointments as Did Not Attend.
- Mark appointments as Approved.

The following fields are NOT editable by students:

- Preferred Date
- Preferred Time Slot
- Appointment Category
- Appointment Mode
- Reason

Students may only:

- Cancel appointments.
- Reschedule appointments.

Rescheduling is treated as:

Current Appointment
↓

Cancelled

↓

Create New Appointment Request

↓

Appointment Conflict Detection

↓

Pending Staff Review

The system SHALL NOT support direct appointment editing.

---

# APPOINTMENT CONFLICT DETECTION

The system shall check:

Preferred Date

+

Preferred Time Slot

If an existing appointment is:

- Pending
- Approved

The system displays:

> This schedule is already taken.

The appointment shall NOT be created.

Conflict detection applies to ALL appointment sources.

---

# STAFF APPOINTMENT DASHBOARD

Dashboard Cards:

- Total Appointments Today
- Pending Requests
- Completed Today

Sections:

- Appointment Requests
- Today's Appointments
- Appointment History
- Flagged Cases Requiring Appointment
- Manual Appointment Entry

The previous slot management system shall be removed.

---

# MANUAL APPOINTMENTS

Manual appointments support:

- Walk-in
- Messenger
- Hotline
- Email

Manual appointments:

- Automatically become Approved.

Students MUST have existing accounts before appointments can be created.

Guest appointments are NOT supported.

---

# COUNSELOR NOTES

Counselor Notes are only editable by Staff users.

Requirements:

Optional:

- Approved
- Did Not Attend
- Cancelled

NOT ALLOWED:

- Pending

Required:

- Done

Counselor Notes form part of the student's appointment history.

---

# RESOLVED CASES MODULE

The Resolved module represents:

- Completed counseling sessions
- Resolved flagged cases
- Completed student interventions
- Completed appointments

Resolved cases are NOT limited to appointments.

---

# CONVERSATION MANAGEMENT

Students SHALL NOT manually end conversations.

The following buttons SHALL NOT exist in production:

- End Conversation
- Export Conversation

Conversation management is fully automatic.

The system determines when conversations end through:

- User inactivity
- Session timeout
- Logout
- Appointment submission

---

# DATA PRIVACY PHILOSOPHY

CTRL4 adopts a Privacy-by-Design architecture.

The system SHALL NOT permanently store:

- Raw student conversations
- Raw chatbot responses
- Conversation transcripts
- Message-by-message chat logs

Conversations are processed temporarily during active sessions.

The system only permanently stores:

- AI Counselor Intake Summaries
- Appointment Records
- Counselor Notes
- Flagged Case Metadata
- Reports and Analytics

Raw conversations are automatically deleted after summarization.

---

# AI COUNSELOR INTAKE SUMMARY

The AI Summary is NOT a generic chatbot summary.

The system generates a structured Counselor Intake Summary consisting of:

- Primary Concern
- Conversation Type
- Emotion Detection Results
- Flagged Status
- Appointment Recommendation
- Suggested Intervention
- Conversation Statistics
- Structured Summary

The AI Summary is generated using the complete conversation context before temporary data is deleted.

---

# STAFF SETTINGS

Staff users may edit:

## Guidance Office Information

- Office Name
- Office Hours
- Office Email
- Office Contact Number
- Office Location

---

## Appointment Settings

- Appointment Categories
- Appointment Modes
- Available Time Slots
- Office Days

---

## Guidance Counselor Settings

- Assigned Programs
- Office Assignment
- Support Statement
- Consultation Rooms
- Consultation Schedules

---

## AI Chatbot Settings

- Auto Flagging
- Escalation Message
- Support Message

---

## Knowledge Base Settings

- FAQs
- Guidance Services
- Policies
- Student Survival Guide Information

---

# REPORTS AND ANALYTICS

Reports include:

Appointments:

- Total Appointments
- Pending
- Approved
- Completed
- Cancelled
- Did Not Attend

Programs:

- Appointment Statistics per Program

Counselors:

- Appointment Statistics per Counselor

Flagged Cases:

- Negative Emotion Statistics
- Escalated Cases
- Resolved Cases

Conversation Statistics:

- Conversation Types
- Appointment Recommendations
- General Inquiry Statistics

---

# LOCKED DESIGN DECISIONS

The following decisions are FINAL:

- Program-based counselor assignment.
- Manual appointment support.
- Privacy-by-Design architecture.
- Temporary conversation storage.
- Automatic conversation management.
- Structured AI Counselor Intake Summaries.
- No End Conversation button.
- No Export Conversation button.
- No appointment slot management system.
- No Rejected appointment status.
- Staff manages Guidance Office operations.
- Admin manages system administration.
- Appointment settings are editable by staff users.
- Academic programs are fixed system constants.
- CTRL4 is an AI-Powered Guidance Office Management System.
- Students may cancel or reschedule their own appointments.
- Students cannot cancel or reschedule appointments that are scheduled within the next 1 hour.
- The 1-hour appointment modification restriction applies only to students.
- Staff users may manage appointments regardless of the remaining time before the scheduled appointment.
- Students SHALL NEVER directly edit appointment information.
- Rescheduling is implemented by cancelling the current appointment and creating a new appointment request.
- Direct appointment editing is not supported.

---

# APPLICATION DESIGN STANDARDS

The following standards apply consistently across all modules of CTRL4 MK II.

## Forms

- Save buttons remain disabled until valid changes are detected.
- Save buttons are disabled again after a successful save.
- Required fields are clearly indicated.
- Real-time validation is performed before submission.

## Modals

- Prompt users before discarding unsaved changes.
- Confirmation dialogs are required for destructive actions.
- ESC closes the modal when appropriate.
- Enter triggers the primary action when the form is valid.

## Tables

- Support search for large datasets.
- Support sorting where applicable.
- Support pagination for long lists.

## Notifications

- Success, warning, and error messages use toast notifications.
- Browser alert dialogs should be avoided except for critical failures.

## Loading and Empty States

- Display loading indicators while data is being retrieved.
- Display informative empty-state messages instead of blank screens.

## Accessibility and Consistency

- Maintain consistent button placement throughout the system.
- Use consistent labels, icons, colors, and interaction patterns.
- Keyboard navigation should be supported where practical.

---

# DEVELOPMENT SPRINTS

Sprint 1

- Appointment Form
- Completed

Sprint 2

- Database Refactor

Sprint 3

- Backend Refactor

Sprint 4

- Conflict Detection

Sprint 5

- Appointment Status Workflow

Sprint 6

- Staff Appointment Dashboard

Sprint 7

- Manual Appointment Entry

Sprint 8

- Appointment Settings

Sprint 9

- Counselor Notes

Sprint 10

- Reports and Analytics

Sprint 11

- Testing and Evaluation

---

# THESIS REMINDER

Never forget:

> CTRL4 MK II is an AI-Powered Guidance Office Management System with an Integrated Guidance Chatbot designed to support inquiry management, negative emotion detection, appointment management, student case management, and guidance counselor support services while preserving student privacy through temporary conversation processing and data minimization.