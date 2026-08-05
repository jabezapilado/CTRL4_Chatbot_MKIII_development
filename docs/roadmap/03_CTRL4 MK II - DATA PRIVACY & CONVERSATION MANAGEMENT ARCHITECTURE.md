# CTRL4 MK II - DATA PRIVACY & CONVERSATION MANAGEMENT ARCHITECTURE

> **Historical planning document.** Current frozen implementation references:
> [Project Context](../architecture/project_context.md) and
> [Project Architecture](../architecture/project_architecture.md).

> This document defines the conversation lifecycle, data privacy architecture, AI summary generation, and temporary data handling of CTRL4 MK II.

---

# DESIGN PHILOSOPHY

CTRL4 adopts the following principles:

- Privacy-by-Design
- Data Minimization
- Confidentiality of Guidance-related Information
- Temporary Processing of Sensitive Information
- Role-Based Access Control
- Need-to-Know Access

The system was intentionally designed to minimize the amount of sensitive student information that is permanently stored.

---

# CONVERSATION MANAGEMENT PHILOSOPHY

Students should interact with CTRL4 naturally.

Students SHALL NOT:

- Manually end conversations.
- Export conversations.
- Manage conversation history.


The system SHALL automatically manage the entire conversation lifecycle.

The active conversation is maintained throughout the authenticated user session.

Students may freely navigate between system pages or refresh the page without losing the active conversation.

Conversation continuity is automatically restored while the authenticated session remains valid.

---

# CONVERSATION LIFECYCLE

The conversation lifecycle is as follows:

```
Student starts conversation
        ↓
Temporary conversation storage
        ↓
Real-time NLP processing
        ↓
Emotion detection
        ↓
Topic classification
        ↓
Appointment detection
        ↓
Flagged case detection
        ↓
Active authenticated session
        ↓
Page navigation / Page refresh (optional)
        ↓
Conversation restored
        ↓
Conversation becomes inactive
        ↓
AI Counselor Intake Summary generation
        ↓
Save summary and metadata
        ↓
Delete temporary conversation data
        ↓
Conversation permanently removed
```

---

# CONVERSATION STATES

The following conversation states are used internally:

```
ACTIVE

↓

WAITING

↓

RESTORED

↓

INACTIVE

↓

SUMMARIZED

↓

DELETED
```

Definitions:

### ACTIVE

- Student is currently chatting.

### WAITING

- No recent activity detected.

### RESTORED

- The active conversation has been automatically restored after page navigation or page refresh while the authenticated session remains valid.

### INACTIVE

- Conversation is considered complete.

### SUMMARIZED

- AI summary generation has been completed.

### DELETED

- Temporary conversation data has been permanently removed.

---

# TEMPORARY CONVERSATION STORAGE

Raw conversations are temporarily stored ONLY during active sessions.

Examples include:

- Session storage
- Temporary server memory
- Temporary application storage

Temporary storage SHALL NOT be considered permanent storage.

Temporary conversation storage exists solely to preserve conversational context during the authenticated session. It is automatically restored after page navigation or refresh and is permanently removed after conversation finalization.

---

# PERMANENT STORAGE POLICY

The following information SHALL be permanently stored:

## Conversation Metadata

- Conversation Type
- Emotion Detection Results
- Appointment Recommendation
- Flagged Status
- Conversation Statistics

---

## AI Counselor Intake Summary

- Primary Concern
- Structured Summary
- Suggested Intervention
- Recommendations

---

## Appointment Records

- Appointment Information
- Appointment Status
- Counselor Notes

---

## Reports and Analytics

- Appointment statistics
- Flagged case statistics
- Conversation statistics
- Program statistics

---

# INFORMATION THAT SHALL NEVER BE STORED

The following information SHALL NOT be permanently stored:

- Raw student conversations
- Raw chatbot responses
- Conversation transcripts
- Message-by-message history
- Conversation exports
- Deleted conversations

Once deleted, the conversation SHALL NOT be recoverable.

---

# AUTOMATIC CONVERSATION TERMINATION

The system automatically determines when a conversation has ended.

Triggers include:

- User inactivity
- Logout
- Session timeout

No user action is required.

The following events SHALL NOT terminate an active conversation:

- Page navigation
- Page refresh
- Returning from the appointment form

---

# CHATBOT USER INTERFACE

The following buttons SHALL NOT exist in production:

REMOVE:

- End Conversation
- Export Conversation

The chatbot interface should remain simple and student-friendly.

---

# REAL-TIME NLP PROCESSING

During an active conversation, the system performs:

- Negative Emotion Detection
- Topic Classification
- Intent Detection
- Appointment Detection
- Flagged Case Detection

Processing occurs in real time during the conversation.

---

# NEGATIVE EMOTION DETECTION

The system shall analyze conversations for negative emotional indicators.

Examples include:

- Sadness
- Anxiety
- Stress
- Loneliness
- Frustration
- Emotional Distress

Negative emotion detection may result in:

- Flagged cases
- Appointment recommendations
- Counselor intervention recommendations

---

# TOPIC CLASSIFICATION

Examples include:

- General Inquiry
- Guidance Services
- Academic Concern
- Emotional Support Concern
- Appointment Inquiry
- Office Information
- Counseling Concern

Topic classification assists in:

- AI Summary generation
- Appointment recommendations
- Flagged case monitoring

---

# AI COUNSELOR INTAKE SUMMARY

The AI Summary is NOT intended to replace counselor judgment.

The AI Summary is designed to assist guidance counselors by providing structured information.

The AI Summary consists of:

## Student Information

- Student Number
- Program
- Date and Time

---

## Conversation Classification

Examples:

- General Inquiry
- Counseling Concern
- Appointment Inquiry
- Academic Concern

---

## Primary Concern

Examples:

- Academic stress
- Difficulty balancing responsibilities
- Emotional distress
- Counseling request

---

## Emotion Detection Results

Examples:

- Sadness
- Anxiety
- Stress

---

## Flagged Status

Values:

- YES
- NO

---

## Appointment Recommendation

Values:

- YES
- NO

---

## Suggested Intervention

Examples:

- Academic Counseling
- Follow-up Counseling Session
- Emotional Support Counseling
- No intervention required

---

## Conversation Statistics

Examples:

- Total Messages
- Language Used
- Appointment Requested

---

## Structured Summary

The AI generates a structured counselor-friendly summary using the complete conversation context.

---

# CONVERSATION ACCURACY REQUIREMENTS

The AI Summary SHALL:

- Consider the complete conversation context.
- Accurately identify the student's primary concern.
- Preserve important contextual information.
- Avoid hallucinated details.
- Provide counselor-friendly recommendations.

The AI Summary SHALL NOT:

- Use only the last few messages.
- Ignore important contextual information.
- Generate unsupported conclusions.

---

# FLAGGED CASE WORKFLOW

```
Student Conversation
        ↓
Negative Emotion Detection
        ↓
Flagged Case Generated
        ↓
AI Summary Generated
        ↓
Conversation Deleted
        ↓
Counselor Review
        ↓
Intervention
        ↓
Resolved Case
```

---

# APPOINTMENT WORKFLOW

```
Student Conversation
        ↓
Appointment Requested
        ↓
Appointment Submitted
        ↓
Conversation Continues
        ↓
Logout / Inactivity Timeout
        ↓
AI Counselor Intake Summary Generated
        ↓
Temporary Conversation Deleted
        ↓
Appointment Record Retained
        ↓
Counselor Review
        ↓
Appointment Completed
```

Submitting an appointment request does not finalize the active conversation. The conversation remains active throughout the authenticated session and is finalized only after logout, session timeout, or prolonged inactivity.

The counselor shall only see:

- Appointment Details
- AI Summary
- Counselor Notes
- Appointment History

The original conversation SHALL NOT be accessible.

---

# STUDENT PRIVACY PROTECTION

Students are protected through:

- Temporary conversation processing.
- Automatic deletion of raw conversations.
- Role-based access control.
- Data minimization.
- Confidential handling of counseling information.

Only the minimum information necessary for Guidance Office operations is permanently retained.

---

# ROLE-BASED ACCESS

## Students

May access:

- Their own appointments.
- Appointment statuses.

Cannot access:

- Counselor notes.
- Other student information.

---

## Staff

May access:

- AI summaries.
- Appointment records.
- Flagged cases.
- Counselor notes.
- Reports.

Cannot access:

- Deleted conversations.

---

## Admin

May access:

- Accounts.
- System administration features.

Cannot access:

- AI summaries.
- Counselor notes.
- Flagged cases.
- Deleted conversations.
- Guidance Office operational records.

---

# DATA PRIVACY ACT COMPLIANCE

CTRL4 was designed to support:

- Data minimization.
- Confidentiality of student information.
- Need-to-know access principles.
- Secure handling of guidance-related information.

The system intentionally limits the amount of sensitive student information that is permanently retained.

---

# LOCKED DESIGN DECISIONS

The following decisions are FINAL:

- Conversations are temporarily stored.
- Raw conversations are automatically deleted.
- Students do not manually end conversations.
- AI summaries are automatically generated.
- AI summaries are counselor-friendly and structured.
- Deleted conversations are not recoverable.
- Only metadata and summaries are permanently retained.
- Privacy-by-Design principles are enforced throughout the system.
- CTRL4 prioritizes student confidentiality and data minimization.
- Active conversations persist only during authenticated sessions.
- Page navigation and page refresh do not terminate active conversations.
- Active conversations are automatically restored while the authenticated session remains valid.
- Temporary conversation storage exists only to preserve conversational context.
- Conversation finalization occurs only after logout or inactivity timeout.
