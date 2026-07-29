# CTRL4 MK II - MASTER DEVELOPMENT ROADMAP

> Thesis Title:
>
> Development of an AI-Powered Chatbot for Inquiry Management Using NLP-Based Negative Emotion Detection
>
> System Name:
>
> CTRL4 MK II

---

# IMPORTANT REMINDER

CTRL4 is NOT just an AI chatbot.

CTRL4 is an:

> AI-Powered Guidance Office Management System with an Integrated Guidance Chatbot

The chatbot is only ONE major component of the entire system.

The system consists of four major modules:

---

# SYSTEM MODULES

## 1. AI Chatbot Module

Features:

- Guidance-related inquiries
- NLP-based Negative Emotion Detection
- Knowledge Base (RAG)
- FAQs
- Academic Support
- Guidance Services
- Conversation Summaries
- Escalation Handling
- Office Information
- Appointment Booking Interface

---

## 2. Appointment Management Module

Features:

- Appointment Booking
- Appointment Conflict Detection
- Manual Appointment Entry
- Appointment Monitoring
- Appointment Status Workflow
- Counselor Notes
- Appointment Analytics
- Appointment Settings
- Appointment History
- Appointment Source Tracking

---

## 3. Guidance Office Management Module

Features:

- Student Account Management
- Staff Account Management
- Flagged Cases
- Conversation Summaries
- Reports
- Guidance Office Information
- Settings Management
- Appointment Management
- Appointment Monitoring

---

## 4. Guidance Counselor Support Module

Features:

- Counselor Notes
- Appointment Records
- Flagged Student Conversations
- Follow-up Recommendations
- Student Appointment History
- Manual Interventions

---

# USER ROLES

## STUDENT

Capabilities:

- Use the AI Chatbot
- Ask Guidance-related questions
- Book appointments
- View appointment details
- Receive appointment updates

---

## STAFF (Guidance Counselors)

Capabilities:

- Manage appointments
- Create manual appointments
- Monitor appointments
- Review flagged cases
- Add counselor notes
- Manage appointment settings
- View appointment records
- View reports
- Manage Guidance Office information

---

## ADMIN (ITSS)

Capabilities:

- Create student accounts
- Create staff accounts
- Edit accounts
- Disable accounts
- Manage system access

Admins SHOULD NOT:

- Manage appointments
- Manage counselor notes
- Manage Guidance Office settings
- Manage appointment categories
- Manage appointment statuses

Those belong to STAFF users.

---

# APPOINTMENT MANAGEMENT SYSTEM

## Appointment Sources

Students may create appointments through:

- Chatbot

Staff may create appointments through:

- Walk-in
- Hotline
- Messenger
- Email

All appointment sources MUST use the same conflict detection algorithm.

---

# APPOINTMENT WORKFLOW

## Chatbot Appointment Workflow

```
Student
↓

Book Appointment

↓

Submit Appointment Request

↓

Pending

↓

Staff Reviews

↓

Approved

↓

Done

OR

Did Not Attend

OR

Cancelled
```

---

## Manual Appointment Workflow

```
Walk-in

OR

Messenger

OR

Hotline

OR

Email

↓

Staff Creates Appointment

↓

Automatically Approved

↓

Done

OR

Did Not Attend

OR

Cancelled
```

---

# FINAL APPOINTMENT STATUSES

```
Pending

Approved

Done

Did Not Attend

Cancelled
```

NO REJECTED STATUS.

This is aligned with Sir Ryan's adviser notes.

---

# FINAL APPOINTMENT FORM

Students should ONLY provide:

- Contact Number
- Appointment Category
- Appointment Mode
- Preferred Date
- Preferred Time Slot
- Reason

The system should automatically retrieve:

- Student Name
- Student Number
- Student Email
- Program
- Role

through the authenticated account.

---

# FINAL APPOINTMENTS TABLE DESIGN

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

    appointment_source VARCHAR(50) NOT NULL,

    created_at DATETIME NOT NULL,

    FOREIGN KEY (account_id)
    REFERENCES accounts(id)

);
```

---

# APPOINTMENT SOURCES

```
chatbot
walk_in
hotline
messenger
email
```

These should be stored in the database.

---

# APPOINTMENT CONFLICT DETECTION

Before creating an appointment, the system must check:

```
Preferred Date
+
Preferred Time Slot
```

If an appointment already exists with:

```
Pending

OR

Approved
```

Display:

```
This schedule is already taken.
```

This applies to:

- Chatbot appointments
- Manual appointments

NO EXCEPTIONS.

---

# APPOINTMENT CATEGORIES

Current categories:

- Home and Family
- Relationships with Peers/Opposite Sex
- Personality Development
- Career/Schooling
- Religion/Spiritual Development
- Health and Recreation
- Employment
- Others

These should be editable by STAFF users.

---

# APPOINTMENT MODES

```
Online
Onsite
```

These should be editable by STAFF users.

---

# AVAILABLE TIME SLOTS

Current time slots:

```
8:00 AM

9:00 AM

10:00 AM

1:00 PM

2:00 PM

3:00 PM
```

These should be editable by STAFF users.

---

# OFFICE DAYS

Examples:

```
Monday
Tuesday
Wednesday
Thursday
Friday
```

These should also be editable by STAFF users.

---

# STAFF APPOINTMENT DASHBOARD

REMOVE:

```
Total Slots

Available Slots

Reserved Slots

Appointment Availability

Add Availability Slot

Mark Available
```

These no longer align with the thesis scope.

---

# NEW STAFF APPOINTMENT DASHBOARD

Replace it with:

```
Appointments

---------------------------------

Total Appointments Today

Pending Requests

Completed Today

---------------------------------

Appointment Requests

---------------------------------

Today's Appointments

---------------------------------

Manual Appointment Entry
```

---

# MANUAL APPOINTMENT ENTRY

Staff should be able to create appointments for:

- Walk-in
- Messenger
- Hotline
- Email

Fields:

```
Student Name

Student Number

Date

Time Slot

Appointment Category

Appointment Mode

Reason

Appointment Source
```

These appointments should automatically become:

```
Approved
```

---

# APPOINTMENT DETAILS MODAL

Staff should be able to view:

```
Student Name

Student Number

Program

Contact Number

Appointment Category

Appointment Mode

Preferred Date

Preferred Time Slot

Reason

Status

Counselor Notes
```

---

# COUNSELOR NOTES

Counselor Notes should ONLY be editable by STAFF users.

Examples:

- Student was advised regarding academic concerns.
- Student requested follow-up counseling.
- Student referred for further evaluation.
- Follow-up appointment recommended.

---

# STAFF ACTIONS

## Pending

Available Actions:

- Approve
- Cancel

---

## Approved

Available Actions:

- Done
- Did Not Attend
- Cancelled

---

## Done

Available Actions:

- View Counselor Notes

---

# APPOINTMENT SETTINGS

Move the following into STAFF SETTINGS:

- Appointment Categories
- Appointment Modes
- Available Time Slots
- Office Days

Examples:

```
Monday - Friday

8:00 AM
9:00 AM
10:00 AM
1:00 PM
2:00 PM
3:00 PM
```

This prevents hard-coding values into the system.

---

# APPOINTMENT ANALYTICS

Examples:

```
Total Appointments Today

Pending Requests

Completed Today

Cancelled Appointments

Did Not Attend

Appointments by Source

Appointments by Category
```

Examples:

```
Chatbot - 15

Walk-in - 5

Messenger - 3

Hotline - 2
```

---

# SPRINT ROADMAP

---

## Sprint 1 - Appointment Form

### STATUS

DONE

### COMPLETED

- appointment.html
- Validation logic
- collectFormData()
- New appointment fields

---

## Sprint 2 - Database Refactor

TO DO:

- Redesign appointments table
- Update schema.sql
- Update db.py

---

## Sprint 3 - Backend Refactor

TO DO:

- Update routes.py
- Update save_appointment()
- Update update_appointment_status()

---

## Sprint 4 - Conflict Detection

TO DO:

Implement:

- This schedule is already taken
- Date validation
- Time slot validation
- Duplicate appointment prevention

---

## Sprint 5 - Appointment Status Workflow

TO DO:

Implement:

- Pending
- Approved
- Done
- Did Not Attend
- Cancelled

---

## Sprint 6 - Staff Appointment Dashboard

TO DO:

Implement:

- Total Appointments Today
- Pending Requests
- Completed Today
- Appointment Monitoring

Remove:

- Slot Management

---

## Sprint 7 - Manual Appointment Entry

TO DO:

Implement:

- Walk-in
- Messenger
- Hotline
- Email

Manual appointment creation.

---

## Sprint 8 - Appointment Settings

TO DO:

Implement editable:

- Appointment Categories
- Appointment Modes
- Available Time Slots
- Office Days

---

## Sprint 9 - Counselor Notes

TO DO:

Implement:

- Staff Notes
- Appointment Notes
- Follow-up Notes

---

## Sprint 10 - Dashboard Analytics

TO DO:

Implement:

- Appointment Statistics
- Appointment Sources
- Appointment Categories
- Daily Appointment Analytics

---

## Sprint 11 - Testing

TO DO:

Perform:

- Student Testing
- Staff Testing
- Conflict Detection Testing
- Manual Appointment Testing
- Appointment Status Workflow Testing
- Dashboard Testing

---

# ADVISER NOTES CHECKLIST

| Requirement | Status |
|------------|------------|
| Quick Buttons | Planned |
| Book Appointment | Planned |
| Office Hours | Planned |
| Multiple Booking Handling | Planned |
| This Schedule is Already Taken | Planned |
| Done Appointment | Planned |
| Did Not Attend | Planned |
| Appointment Monitoring | Planned |
| Staff Actions | Planned |
| Counselor Notes | Planned |
| Admin Account Management | Planned |
| Flagged Cases | Planned |
| Total Number of Appointments Today | Planned |
| Third-Person Thesis Documentation | Planned |
| Data Privacy Considerations | Planned |
| G*Power Sample Computation | Planned |
| Real-Time Conversation Survey Questions | Planned |

---

# THESIS REMINDER

Never forget:

> CTRL4 MK II is NOT merely an AI chatbot.

It is an:

> AI-Powered Guidance Office Management System with an Integrated Guidance Chatbot for Inquiry Management, NLP-Based Negative Emotion Detection, Appointment Management, and Guidance Counselor Support Services.

All future development decisions should support the Guidance Office Management System as a whole and not just the chatbot module.

---

# WHEN YOU WAKE UP

START WITH:

```
SPRINT 2

DATABASE REFACTOR

1. Redesign appointments table.
2. Update schema.sql.
3. Update db.py.
```

DO NOT TOUCH:

- routes.py
- dashboard pages
- staff pages
- appointment submission logic

until Sprint 2 is completed.

The appointment subsystem architecture is now LOCKED unless new adviser requirements are introduced.