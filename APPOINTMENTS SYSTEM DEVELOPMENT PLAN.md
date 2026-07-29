# CTRL4 MK II - Appointment System Development Plan

## Finalized Architecture

### Appointment Sources

Students should be able to create appointments through:

- Chatbot
- Walk-in (Staff)
- Hotline (Staff)
- Messenger/Social Media (Staff)
- Email (Staff)

All appointment sources should use the SAME scheduling and conflict detection system.

---

## Appointment Workflow

### Chatbot Appointment Workflow

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

### Manual Appointment Workflow

```
Walk-in

OR

Messenger

OR

Hotline

OR

Email

↓

Staff creates appointment

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

## Final Appointment Statuses

```
Pending
Approved
Done
Did Not Attend
Cancelled
```

These are aligned with Sir Ryan's adviser notes.

---

## Final Appointment Form

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

through the authenticated account/session.

---

## Final Appointment Table Design

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

## Appointment Sources (Database)

```
chatbot
walk_in
hotline
messenger
email
```

---

## Conflict Detection

Before creating an appointment, the system should check:

```
Preferred Date
+
Preferred Time Slot
```

If an appointment already exists with the following statuses:

```
Pending
Approved
```

The system should display:

```
This schedule is already taken.
```

This applies to:

- Chatbot appointments
- Manual appointments

No exceptions.

---

## Appointment Categories

Current categories:

- Home and Family
- Relationships with Peers/Opposite Sex
- Personality Development
- Career/Schooling
- Religion/Spiritual Development
- Health and Recreation
- Employment
- Others

These should be editable by STAFF users through Settings.

---

## Appointment Modes

```
Online
Onsite
```

Should also be editable through Settings.

---

## Time Slots

Current:

```
8:00 AM
9:00 AM
10:00 AM
1:00 PM
2:00 PM
3:00 PM
```

Should also be editable by STAFF users.

---

## Staff Appointment Dashboard

### REMOVE

```
Total Slots

Available Slots

Reserved Slots

Appointment Availability

Add Availability Slot

Mark as Available
```

---

## New Staff Appointment Dashboard

Replace it with:

```
Appointments

----------------------------------

Total Appointments Today

Pending Requests

Completed Today

----------------------------------

Appointment Requests

----------------------------------

Today's Appointments

----------------------------------

Manual Appointment Entry
```

---

## Manual Appointment Entry

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

## Appointment Details Modal

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

## Counselor Notes

Should ONLY be editable by STAFF users.

Examples:

- Student was advised regarding academic concerns.
- Student requested follow-up counseling.
- Student referred for further evaluation.

---

## Staff Actions

### Pending

Staff can:

- Approve
- Cancel

---

### Approved

Staff can:

- Done
- Did Not Attend
- Cancelled

---

### Done

Staff can:

- View Counselor Notes

---

## Admin Responsibilities

Admins are NOT Guidance Counselors.

Admins are ONLY responsible for:

- Account Management
- Create Accounts
- Edit Accounts
- Disable Accounts
- Manage System Access

Admins SHOULD NOT:

- Manage Appointments
- Manage Appointment Settings
- Manage Guidance Office Settings
- Manage Counselor Notes

Those belong to STAFF.

---

## Staff Responsibilities

Staff users should manage:

- Appointments
- Appointment Settings
- Appointment Categories
- Appointment Modes
- Available Time Slots
- Office Information
- Counselor Notes
- Appointment Monitoring
- Flagged Cases
- Reports

---

## Appointment Settings

Move the following into Staff Settings:

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

# SPRINT ROADMAP

---

## Sprint 1 - Appointment Form

### STATUS

```
DONE
```

### COMPLETED

- appointment.html
- Validation logic
- collectFormData()
- New appointment form fields

---

## Sprint 2 - Database Refactor

### TO DO

- Redesign appointments table.
- Update schema.sql.
- Update db.py.

---

## Sprint 3 - Backend Refactor

### TO DO

- Update routes.py.
- Update save_appointment().
- Update update_appointment_status().

---

## Sprint 4 - Conflict Detection

### TO DO

Implement:

- This schedule is already taken.
- Date validation.
- Time slot validation.
- Duplicate appointment prevention.

---

## Sprint 5 - Appointment Status Workflow

### TO DO

Implement:

- Pending
- Approved
- Done
- Did Not Attend
- Cancelled

---

## Sprint 6 - Staff Appointment Dashboard

### TO DO

- Remove slot management.
- Implement appointment monitoring.

---

## Sprint 7 - Manual Appointment Entry

### TO DO

Implement manual appointment creation for:

- Walk-in
- Messenger
- Hotline
- Email

---

## Sprint 8 - Appointment Settings

### TO DO

Implement editable:

- Appointment Categories
- Appointment Modes
- Available Time Slots
- Office Days

---

## Sprint 9 - Counselor Notes

### TO DO

Implement:

- Staff Notes
- Appointment Notes
- Follow-up Notes

---

## Sprint 10 - Dashboard Analytics

### TO DO

Implement:

- Total Appointments Today
- Pending Requests
- Completed Today
- Appointment Statistics

---

## Sprint 11 - Testing

### TO DO

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
| Multiple Booking Handling | To Implement |
| This Schedule is Already Taken | To Implement |
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

# IMPORTANT REMINDERS

Before proceeding with Sprint 2:

DO NOT:

- Modify routes.py
- Modify db.py
- Modify schema.sql
- Modify the staff dashboard
- Test appointment submission

The frontend appointment form is already in a good state.

---

# TOMORROW'S FIRST TASK

```
Sprint 2 - Database Refactor

1. Redesign the appointments table.
2. Update schema.sql.
3. Update db.py.
```

The appointment subsystem architecture is now finalized and should serve as the basis for all future backend and frontend changes unless new adviser requirements are introduced.