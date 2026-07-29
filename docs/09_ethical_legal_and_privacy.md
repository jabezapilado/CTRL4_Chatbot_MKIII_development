# CTRL4 Chatbot MK II
## 09 — Ethical, Legal, and Privacy Considerations

**Version:** MK II Stable (v2.1.0)

**Authors**

- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell

**Capstone Project**

Development of an AI-Powered Guidance Chatbot for Inquiry Management Using NLP-Based Negative Emotion Detection

**Institution**

Holy Angel University

**Program**

Bachelor of Science in Computer Science

**Academic Year**

2026–2027

**Last Updated**

July 2026

---

# Purpose

CTRL4 was developed as an AI-assisted Guidance Office support system intended to provide immediate assistance to students while supporting licensed Guidance Counselors in identifying students who may require professional intervention.

The system was intentionally designed to complement, rather than replace, professional counseling services. Ethical principles, privacy protection, and responsible AI development were considered throughout the system design process.

---

# Ethical Design Philosophy

The development of CTRL4 follows five major principles:

- Privacy
- Confidentiality
- Human Oversight
- Responsible AI
- Student Safety

These principles influenced every architectural decision made during the development of the system.

---

# Philippine Legal Framework

---

# Republic Act No. 10173

## Data Privacy Act of 2012

The Data Privacy Act of 2012 is the primary Philippine law governing the collection, storage, processing, and protection of personal information.

CTRL4 processes student information including:

- Student Name
- Student ID
- University Email
- Appointment Requests
- AI Conversations
- Emotional Indicators
- Guidance Concerns

Because the system processes personal data, compliance with Republic Act No. 10173 is essential.

---

## Data Privacy Principles

CTRL4 follows the three core principles of the Data Privacy Act.

### Transparency

Students are informed that:

- they are communicating with an AI assistant;
- conversations may be processed to provide assistance;
- flagged cases may require Guidance Office intervention according to institutional policy.

---

### Legitimate Purpose

Information is collected solely for legitimate Guidance Office purposes including:

- providing student support;
- scheduling appointments;
- identifying high-risk situations;
- improving guidance services.

CTRL4 does not collect unnecessary information unrelated to these purposes.

---

### Proportionality

Only information necessary to assist students is processed.

The chatbot avoids requesting excessive personal information unless required for Guidance Office services.

---

# Implementing Rules and Regulations (IRR)

CTRL4 aligns with the Implementing Rules and Regulations of the Data Privacy Act through:

- secure authentication;
- access control;
- role separation;
- controlled administrative access;
- protection against unauthorized disclosure.

---

# National Privacy Commission

The National Privacy Commission (NPC) promotes two important concepts.

## Privacy by Design

Privacy is incorporated during system development rather than added afterward.

Examples within CTRL4 include:

- role-based permissions;
- limited data collection;
- restricted dashboard access;
- secure authentication.

---

## Privacy by Default

The system protects student privacy by default.

Examples include:

- conversations remain confidential;
- only necessary information is displayed to Guidance personnel;
- administrative permissions are restricted according to responsibilities.

---

# Republic Act No. 9258

## Philippine Guidance and Counseling Act of 2004

Republic Act No. 9258 regulates the professional practice of Guidance and Counseling in the Philippines.

CTRL4 was intentionally designed **not** to replace licensed Guidance Counselors.

Instead, the system:

- answers common Guidance Office questions;
- provides general emotional support;
- encourages healthy coping strategies;
- recommends professional assistance when appropriate;
- identifies students who may require intervention.

Professional assessment, counseling, and decision-making remain the responsibility of licensed Guidance Counselors.

---

# Republic Act No. 11036

## Philippine Mental Health Act

The Mental Health Act promotes accessible mental health services while protecting individual dignity and confidentiality.

CTRL4 supports this law by:

- encouraging professional help when appropriate;
- avoiding medical or psychological diagnosis;
- avoiding treatment recommendations;
- promoting healthy coping strategies;
- assisting students in accessing Guidance Office services.

---

# Confidentiality

Confidentiality is a fundamental principle in Guidance and Counseling.

CTRL4 was designed so that student concerns remain confidential unless intervention is required according to institutional policy.

---

# Privacy Model

The system follows the principle of **least privilege**.

Access is granted only to information necessary for each user's responsibilities.

---

## Student

Students may:

- communicate with CTRL4;
- schedule appointments;
- manage their own profile;
- access their own records.

Students cannot access other students' information.

---

## Guidance Staff

Guidance Staff may:

- review flagged cases;
- update case status;
- record counselor notes;
- manage appointments.

Staff members should only access information necessary for professional intervention.

---

## Administrator

Administrators may:

- create student accounts;
- manage staff accounts;
- manage administrator accounts;
- manage system settings;
- generate reports;
- oversee flagged cases.

Administrative privileges should follow institutional policies and the principle of least privilege.

---

# Role-Based Access Control

CTRL4 implements Role-Based Access Control (RBAC) to minimize unauthorized access.

RBAC provides:

- improved confidentiality;
- reduced security risks;
- clear separation of responsibilities;
- accountability.

---

# AI Decision Support

CTRL4 functions as a **decision-support system** rather than an autonomous decision-maker.

The AI assists Guidance Counselors by:

- identifying concerning conversations;
- classifying emotional states;
- retrieving official Guidance Office information;
- recommending appropriate follow-up.

Final decisions remain with human Guidance Counselors.

---

# Crisis Detection

CTRL4 includes crisis detection capabilities.

Examples include:

- possible suicidal ideation;
- self-harm indicators;
- severe emotional distress;
- immediate safety concerns.

When such situations are detected, the system recommends professional intervention.

---

# Flagged Case Workflow

The intended workflow is:

Student

↓

CTRL4 AI

↓

Routine Concern

↓

Conversation Ends

OR

↓

Potential Crisis Detected

↓

Flagged Case Created

↓

Guidance Dashboard

↓

Licensed Guidance Counselor Reviews Case

↓

Student Contacted Through Official University Channels

↓

Case Resolved

This workflow ensures that professional intervention remains human-led.

---

# Why Live Takeover Was Removed

Early versions of CTRL4 considered allowing Guidance personnel to take over live AI conversations.

After evaluation, this feature was removed because it introduced significant concerns regarding:

- student privacy;
- confidentiality;
- informed consent;
- ethical AI practices.

Instead, CTRL4 creates **Flagged Cases** that notify Guidance personnel when intervention may be appropriate.

Counselors contact students through official university communication channels rather than entering ongoing AI conversations.

This design better respects confidentiality while maintaining student safety.

---

# Human Oversight

Human oversight remains essential.

CTRL4 does **not**:

- diagnose mental illness;
- replace counselors;
- prescribe treatment;
- make disciplinary decisions;
- perform psychological assessments.

The system only provides recommendations based on available information.

---

# Ethical AI Principles

CTRL4 follows widely recognized ethical AI principles.

## Transparency

Students are informed when interacting with an AI assistant.

---

## Accountability

Human counselors remain responsible for all professional decisions.

---

## Fairness

The system should provide equal assistance regardless of:

- gender;
- religion;
- ethnicity;
- disability;
- socioeconomic status.

---

## Privacy

Student information is protected throughout the system lifecycle.

---

## Security

Appropriate technical safeguards protect stored information.

---

## Non-Maleficence

The AI should avoid causing harm by:

- avoiding dangerous advice;
- avoiding false diagnoses;
- encouraging professional assistance when appropriate.

---

## Beneficence

CTRL4 aims to improve student well-being by:

- providing immediate support;
- reducing barriers to Guidance services;
- encouraging early intervention.

---

# Limitations

CTRL4 has several intentional limitations.

The system:

- cannot replace licensed Guidance Counselors;
- cannot diagnose mental illness;
- may misunderstand ambiguous language;
- depends on available knowledge base information;
- should not be used during medical emergencies.

---

# Future Ethical Improvements

Future versions of CTRL4 may include:

- multilingual ethical AI models;
- explainable AI decisions;
- improved crisis detection;
- stronger privacy controls;
- encrypted conversation storage;
- audit logging;
- consent management.

---

# Recommended System Policies

The following policies are recommended for institutional deployment.

1. Student conversations are confidential.
2. CTRL4 supplements licensed counselors rather than replacing them.
3. Flagged cases are reviewed by authorized Guidance personnel.
4. Students are contacted using official university communication channels.
5. Role-Based Access Control limits access to sensitive information.
6. Administrative privileges follow the principle of least privilege.
7. Students receive clear privacy notices before using the chatbot.
8. AI recommendations remain advisory only.

---

# Ethical Statement

CTRL4 was designed in accordance with Philippine privacy laws, ethical AI principles, and responsible Guidance Office practices.

The system protects student confidentiality through role-based access control, limits access to sensitive information, maintains human oversight for all counseling-related decisions, and supports licensed Guidance Counselors by providing intelligent decision support rather than autonomous counseling.

---

# References

## Philippine Laws

Republic Act No. 10173 — Data Privacy Act of 2012

Republic Act No. 9258 — Philippine Guidance and Counseling Act of 2004

Republic Act No. 11036 — Philippine Mental Health Act

---

## Philippine Government Agencies

National Privacy Commission

https://privacy.gov.ph

Official Gazette of the Republic of the Philippines

https://www.officialgazette.gov.ph

---

## International References

UNESCO. (2021). Recommendation on the Ethics of Artificial Intelligence.

National Institute of Standards and Technology (NIST). AI Risk Management Framework (AI RMF 1.0).

ISO/IEC 27001:2022. Information Security Management Systems.

IEEE. Ethically Aligned Design for Autonomous and Intelligent Systems.

OECD Principles on Artificial Intelligence.