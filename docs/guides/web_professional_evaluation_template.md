# Web Professional Evaluation Template

**System:** CTRL4 Chatbot MK III<br>
**Evaluator:** [Name, organization, and web/UX/accessibility role]<br>
**Evaluation date:** [YYYY-MM-DD]<br>
**Build or release reviewed:** [for example, v1.0.7]<br>
**Status:** Draft review form; completing it does not change the application,
accounts, settings, appointments, or student records.

## Purpose

Use this form to obtain an independent web-development, UX, and accessibility
review of the student, counselor, and administrator interfaces. The reviewer
should use designated test accounts and synthetic test data only. They must
not alter real appointments, safety cases, counselor settings, or accounts.

## Reviewer instructions

1. Record each result with the viewport, browser, route, and observed outcome.
2. Test the student, staff, and administrator views separately. Verify that a
   role sees only the screens and data it is authorized to access.
3. Do not enter real personal, health, or crisis information. Use approved
   synthetic test messages and test accounts.
4. Mark an issue as **Blocker**, **Major**, **Minor**, or **Observation**.
   A Blocker includes a privacy exposure, broken authentication/CSRF/Terms
   gate, inaccessible core task, or unusable safety workflow.
5. Do not change production data or settings as part of the review. Describe
   a proposed change in the findings register instead.

## Relationship to the official ISO/IEC questionnaire

The official numerical result belongs in the approved **ISO/IEC 25010:2023
Software Quality Evaluation — Web Expert Questionnaire** (Google Form). This
template does **not** repeat that questionnaire's 1–5 scale. Use it to record
the browser, viewport, route, evidence, and recommended correction behind each
answer.

Use **Observed**, **Needs improvement**, or **Not assessed** here. Record a
finding severity only when there is a problem: **Blocker**, **Major**,
**Minor**, or **Observation**.

| This template section | Official Web questionnaire characteristics it supports |
| --- | --- |
| Student experience | Functional Suitability; Interaction Capability; Safety |
| Counselor workflow and information design | Functional Suitability; Interaction Capability; Reliability; Safety |
| Settings and appointment UX | Functional Suitability; Interaction Capability; Reliability; Security |
| Accessibility and responsive design | Interaction Capability; Safety |
| Frontend security and role boundaries | Security; Reliability; Safety |
| Viewport record | Performance Efficiency; Interaction Capability |

## 1. Student experience

Use the compact **Status** cell to avoid a wide table. Add the
supporting evidence and recommended correction in the final cell.

| Criterion | Status | Evidence and recommended action |
| --- | --- | --- |
| Login, per-session Terms acknowledgement, and logout behave predictably. | [Observed / Needs improvement / Not assessed] | [ ] |
| The chatbot remains usable at desktop, tablet, and mobile viewports. | [Observed / Needs improvement / Not assessed] | [ ] |
| The Terms dialog is visibly centered and usable without hidden or clipped controls. | [Observed / Needs improvement / Not assessed] | [ ] |
| Chat controls, quick replies, feedback controls, and appointment navigation are discoverable. | [Observed / Needs improvement / Not assessed] | [ ] |
| Selected and unselected feedback controls have clear visual states and keyboard focus. | [Observed / Needs improvement / Not assessed] | [ ] |
| Appointment booking, cancellation, and rescheduling communicate request status clearly. | [Observed / Needs improvement / Not assessed] | [ ] |

## 2. Counselor workflow and information design

| Criterion | Status | Evidence and recommended action |
| --- | --- | --- |
| The Inbox makes active, pending-review, reviewed, routine, and finalized items understandable. | [Observed / Needs improvement / Not assessed] | [ ] |
| Active conversations appear without requiring a finalized AI summary. | [Observed / Needs improvement / Not assessed] | [ ] |
| Flagged Cases distinguishes Pending review from Reviewed, and the sidebar count shows pending cases only. | [Observed / Needs improvement / Not assessed] | [ ] |
| Feedback cards, filters, searches, and sortable table headings are consistent with other staff pages. | [Observed / Needs improvement / Not assessed] | [ ] |
| Notification items are opened individually; unread/read state is clear. | [Observed / Needs improvement / Not assessed] | [ ] |
| Clicking the staff logo returns to Inbox home, and browser navigation does not cause a confusing exit path. | [Observed / Needs improvement / Not assessed] | [ ] |

## 3. Settings and appointment UX

| Criterion | Status | Evidence and recommended action |
| --- | --- | --- |
| Global Office Settings and My Staff Settings are clearly separated. | [Observed / Needs improvement / Not assessed] | [ ] |
| Global settings identify shared office information, booking rules, and FAQ content. | [Observed / Needs improvement / Not assessed] | [ ] |
| My Staff Settings identifies counselor-specific availability, rooms, start times, and consultation modes. | [Observed / Needs improvement / Not assessed] | [ ] |
| Foldable settings sections, save controls, form validation, and confirmation messages are understandable. | [Observed / Needs improvement / Not assessed] | [ ] |
| Account Security remains separate from other settings and is accessible only to the signed-in account. | [Observed / Needs improvement / Not assessed] | [ ] |

## 4. Accessibility and responsive design

| Criterion | Status | Evidence and recommended action |
| --- | --- | --- |
| Keyboard-only navigation reaches all core buttons, forms, dialogs, tabs, and table controls. | [Observed / Needs improvement / Not assessed] | [ ] |
| Visible focus states and labels make interactive elements understandable. | [Observed / Needs improvement / Not assessed] | [ ] |
| Text, status colors, badges, and feedback selection do not rely on color alone. | [Observed / Needs improvement / Not assessed] | [ ] |
| Dialogs manage focus, close safely, and remain usable with zoom or narrow screens. | [Observed / Needs improvement / Not assessed] | [ ] |
| Tables remain readable or adapt appropriately on narrow viewports. | [Observed / Needs improvement / Not assessed] | [ ] |
| Logo, buttons, links, and form controls have appropriate accessible names. | [Observed / Needs improvement / Not assessed] | [ ] |

## 5. Frontend security and role boundaries

| Criterion | Status | Evidence and recommended action |
| --- | --- | --- |
| Unauthorized routes redirect safely and do not reveal protected content. | [Observed / Needs improvement / Not assessed] | [ ] |
| Student, counselor, and administrator roles receive only their permitted views. | [Observed / Needs improvement / Not assessed] | [ ] |
| A counselor cannot discover another counselor's program-scoped student data through search, filters, or direct navigation. | [Observed / Needs improvement / Not assessed] | [ ] |
| CSRF-protected mutations and the Terms/session gate remain intact. | [Observed / Needs improvement / Not assessed] | [ ] |
| Browser back/forward behavior preserves a clear application route and does not bypass session controls. | [Observed / Needs improvement / Not assessed] | [ ] |

## Recommended viewport record

| View | Browser and viewport | Result | Notes |
| --- | --- | --- | --- |
| Student desktop | [ ] | [ ] | [ ] |
| Student mobile | [ ] | [ ] | [ ] |
| Counselor desktop | [ ] | [ ] | [ ] |
| Counselor tablet | [ ] | [ ] | [ ] |
| Administrator desktop | [ ] | [ ] | [ ] |

## Findings register

| ID | Finding and evidence | Severity | Recommended action, owner, and retest |
| --- | --- | --- | --- |
| WEB-01 | [ ] | [ ] | Action: [ ]<br>Owner: [ ]<br>Retest: [ ] |
| WEB-02 | [ ] | [ ] | Action: [ ]<br>Owner: [ ]<br>Retest: [ ] |
| WEB-03 | [ ] | [ ] | Action: [ ]<br>Owner: [ ]<br>Retest: [ ] |

## Overall recommendation

- [ ] Approved for the evaluated scope
- [ ] Approved with minor recommendations
- [ ] Re-evaluate after listed corrections
- [ ] Not approved for the evaluated scope

**Summary of required corrections:**

> [Evaluator response]

**Evaluator signature / acknowledgement:** [ ]<br>
**Date:** [ ]

## After review

The development team should turn accepted findings into tracked issues, add an
appropriate regression or frontend contract test, and retest the affected role
and viewport. Security, privacy, and safety findings should be addressed
before any wider student release.
