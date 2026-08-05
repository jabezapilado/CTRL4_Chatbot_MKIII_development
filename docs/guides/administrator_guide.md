# CTRL4 Chatbot MK III — Administrator Guide

> Administrators have account-management authority only. This guide does not
> describe Guidance Office workflows because those records are not available to
> administrator accounts.

## Account management

Use the account-management operations documented in
[API Reference](../architecture/api_reference.md#accounts) to list accounts, apply the
existing role/status filters, and use the approved identifier search. Create
student, staff, or administrator accounts using the fields accepted for the
selected role. Unsupported role-specific fields are rejected rather than
ignored. The `/admin` landing page provides the existing account-listing
interface; it is not a Guidance Office dashboard.

You can update and deactivate student, staff, and administrator accounts using
their dedicated account operations. Administrator accounts cannot retain
student, staff, counselor-profile metadata, or account numbers. You cannot
deactivate your own administrator account.

## Access boundary

Administrator accounts cannot access appointments, appointment lifecycle
controls, counselor notes, case notes, conversations, summaries, escalations,
flagged cases, referrals, interventions, confidentiality records, staff
settings, staff analytics, reports, or CSV exports. Use only the account
management functions assigned to the administrator role.

## Session safety

Sign out after account-management work, especially on shared devices. Login and
logout use the application's server-side session; do not share credentials or
browser cookies.
