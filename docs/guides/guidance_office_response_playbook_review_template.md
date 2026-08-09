# Guidance Office Response Playbook — Review Template

**Status:** Draft for Guidance Office review. This file is deliberately outside
`ai_engine/knowledge_base`, so it is not used by the live chatbot or RAG index.

## Purpose

Capture the School of Computing Guidance Office's preferred student-facing
approach. Use clear, short language that can later be reviewed, approved, and
converted into evidence-backed knowledge-base records.

## Review rules

- Only include practices the Guidance Office has approved.
- Put current contact details, schedules, counselor assignments, and booking
  rules in the application settings, not in this document.
- Do not include student examples, case notes, names, private staff contact
  details, or internal dashboard procedures.
- The chatbot's existing crisis safety response remains authoritative; this
  document must not replace emergency or escalation safeguards.

## How to complete this template

1. Answer only the sections your office can approve today. It is fine to leave
   a section blank or mark it **Needs discussion**.
2. Use 2–4 short sentences for each answer. Write what you would want a
   student to hear, not technical system instructions.
3. Prefer concrete, supportive wording such as **"You may request a counseling
   appointment"** over promises such as **"A counselor will see you today."**
4. Where possible, provide one useful follow-up question. For example,
   **"What feels most difficult right now?"**
5. Mark any wording that must remain exactly as written with **Approved exact
   wording:**. The development team will preserve that wording when it is
   converted to chatbot knowledge.

### Short example

**Student concern:** "I am overwhelmed by my assignments."

> **Preferred response:** "It sounds like you have a lot to manage right now.
> We can identify the most urgent task and choose one small next step. If this
> pressure continues to feel difficult to manage, you may request counseling
> support."
>
> **Follow-up question:** "Which requirement feels most urgent today?"

This example is only a format guide; Guidance Office should replace it with its
own approved wording.

## 1. Opening a support conversation

**When a student opens a general conversation or says they need help:**

> [Guidance Office: provide 2–4 approved sentences or bullet points.]

**Guide:** Begin with reassurance and an invitation to share. Do not diagnose,
minimize the concern, or promise an outcome.

**Appropriate follow-up question(s):**

> [Examples approved by Guidance Office.]

## 2. Academic pressure, burnout, focus, and grades

**Preferred approach:**

> [How staff acknowledge the concern and the practical next step they normally
> encourage.]

**Guide:** State one manageable action the student can take. Explain when it is
appropriate to seek additional Guidance Office support.

**When to suggest a counselor or referral:**

> [Approved indicators and wording.]

## 3. Personal, family, relationship, or peer concerns

**Preferred approach:**

> [Approved supportive framing and boundaries.]

**Guide:** Be respectful and non-judgmental. Do not tell the student what
decision to make about a relationship, family member, or peer.

**Follow-up question(s):**

> [Approved question(s).]

## 4. Counseling requests and appointments

**How to explain the next step without promising availability:**

> [Approved wording.]

**Guide:** Direct students to the Appointment page or official office channels.
Do not state dates, times, counselor assignments, or response times here;
those are kept current by the application settings.

**What the chatbot should never promise:**

> [Examples: same-day availability, a counselor's response time, confidentiality
> limits that have not been approved.]

## 5. Safety concerns

**Non-emergency distress that should be encouraged to seek counselor support:**

> [Approved wording and boundaries.]

**Guide:** Describe only support and referral wording for non-emergencies. The
system already takes over for explicit safety, self-harm, and harm-to-others
messages.

**Important:** Do not paste emergency numbers, escalation internals, or an
alternative crisis script here. Those are maintained separately by the safety
service and approved emergency-contact records.

## 6. Language and tone

**Preferred tone:**

> [For example: formal English, Filipino, Taglish, honorifics, or phrases to
> avoid.]

**Guide:** Specify whether "po," "Ma'am," "Sir," or other local conventions
are appropriate, and give one example of the desired tone if helpful.

**Phrases the Guidance Office does not want used:**

> [List.]

## 7. Approval record

- Reviewer name and role: [ ]
- Review date: [ ]
- Approved for chatbot knowledge base: [Yes / No]
- Required revisions: [ ]

## 8. Urgent-alert and after-hours contact confirmation

**Status:** Planning record only. Completing this section does not change the
chatbot, Inbox, notifications, contact details, or RAG index.

### Urgent case recipient

**Approved routing rule:** The student's program-assigned Guidance counselor
receives the high-priority case for review.

**Counselor review coverage:**

> [List the days/hours when alerts are actively monitored. If no 24/7 coverage
> exists, state that clearly.]

### Public counselor Facebook channels

For each public Facebook page that may be shown to a student, confirm all of
the following before it is used in a future crisis response:

- Counselor/page name: [ ]
- Official page URL: [ ]
- Approved for student contact: [Yes / No]
- Monitored after hours: [Yes / No]
- If yes, monitoring days/hours: [ ]
- Appropriate for urgent messages: [Yes / No]
- Exact student-facing wording: [ ]

**Important:** A public page is not treated as an emergency or 24/7 service
unless the Guidance Office explicitly marks it that way. Emergency resources
remain separate from counselor contact channels.

## After approval

Convert each approved item into a separate, source-attributed JSON record in
`ai_engine/knowledge_base`. Then run the existing ingestion process and its
tests. Do not place this template itself in the knowledge-base folder.
