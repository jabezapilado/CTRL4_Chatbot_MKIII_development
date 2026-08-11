# CTRL4 Chatbot MK III — Student User Guide

> This guide covers only the student workflows currently implemented.

## Sign in and sign out

Sign in at the login page using your authorized account. A successful sign-in
creates a server-side session; sign out when you finish using a shared device.
If your session has expired, sign in again. Do not share passwords or browser
session information. Before chat access, read and accept the Terms and
Conditions for the current session. If you decline, the system signs you out.

## Chatbot

Use the chatbot to ask Guidance Office-related questions in English, Filipino,
or Taglish. The system can provide supportive information, but it does not
diagnose or prescribe treatment. If an immediate safety response is shown,
contact a trusted person or the Guidance Office promptly as instructed.

The Terms apply to the Guidance Office of the School of Computing at Holy Angel
University. They explain that messages may be recorded and summarized for
guidance support and that confidentiality has limits for serious safety or legal
concerns. The chatbot is not an emergency service: if you or someone else is in
immediate danger, contact local emergency services or trusted school personnel.

Language/response rules support Filipino and Taglish interaction, but the
released emotion model is English-focused. Do not interpret Filipino/Taglish
emotion handling as equivalent to a separately validated Filipino or Taglish
emotion model.

Your active chat is used while you converse and for finalization; raw chat
transcript/history is not permanently stored. Do not enter information you do
not need the Guidance Office to handle.

Send one message at a time. While CTRL4 is preparing an ordinary reply, the
message field, **Send** button, and quick-reply buttons are briefly unavailable.
They become available again after the reply. Safety and escalation replies are
not deliberately delayed.

The chat works on current compact mobile and tablet screens. On a narrow phone,
quick reply options may scroll horizontally so their labels remain readable.
When the on-screen keyboard opens, the chat header remains visible and the
composer stays above the keyboard. The student chat prevents accidental
browser zoom while composing so the conversation layout remains stable.

After a chatbot reply, you may select the **like** or **dislike** icon and then
choose a feedback category or optionally leave a short note. Feedback is used
to review recurring quality issues; it is not monitored for emergencies and
does not replace asking for help in the chat or contacting emergency
services/trusted school personnel when there is immediate danger.

## Appointments

Use **My Appointments** to request an appointment with a date and start time.
The system routes the request from your current program to the currently
configured counselor; it does not promise a permanently assigned counselor.

A date/time is unavailable when an existing `pending` or `confirmed`
appointment has the same normalized start time on that date. The message
`This schedule is already taken.` means another active appointment already
uses that start time. The office and counselor schedules can also reject a
request.

Your requested appointment begins as **pending**. Guidance staff may later
confirm, reject, cancel, or complete it. You may cancel or reschedule only
your own pending appointment and only before the one-hour modification
deadline. Rescheduling creates a replacement appointment first and cancels the
old one only after the replacement succeeds.

## Notifications and case status

The notifications panel shows only your own in-app notifications. It opens from
the bell as a popover above the chat header. Opening an appointment notification
marks it as read and takes you to **My Appointments**. Notifications are not
sent by email or SMS.

The **Case Status** page shows only the approved generic progress/status of
your own eligible case. It does not display counselor notes, summaries,
escalation reasons, referrals, interventions, confidentiality information, or
internal identifiers.

## Privacy and common messages

Staff-only counseling records are not available to student accounts. Common
messages include **Login required**, **Student access required**, validation
messages for incomplete forms, and the exact schedule-conflict message above.
If a request fails, correct only the field/message shown and try again; do not
submit confidential information through URL parameters.
