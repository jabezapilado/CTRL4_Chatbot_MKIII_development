# CTRL4 Chatbot MK III — Administrator Guide

> Administrators have account-management authority only. This guide does not
> describe Guidance Office workflows because those records are not available to
> administrator accounts.

Administrators are not guidance-case handlers and do not have chatbot takeover
authority.

## Account management

Use the account-management operations documented in
[API Reference](../architecture/api_reference.md#accounts) to list accounts, apply
the existing role/status filters, and use the approved identifier search. The
`/admin` landing page provides a responsive account-management portal; it is
not a Guidance Office dashboard. Its displayed-account summary always reflects
the accounts returned by the current filters.

The portal supports the approved existing operations:

- create a student, Guidance-staff, or administrator account using the fields
  accepted for the selected role;
- update approved role-specific profile fields; and
- deactivate active accounts using the existing role-specific deactivation
  operation.

Unsupported role-specific fields are rejected rather than ignored. Account
roles are selected when creating an account and are not changed by the current
account-update contract. The current API supports deactivation, not
reactivation or destructive deletion. Password hashes are never shown, and
administrators cannot reset another user's password through this portal.

You can update and deactivate student, staff, and administrator accounts using
their dedicated account operations. Administrator accounts cannot retain
student, staff, counselor-profile metadata, or account numbers. You cannot
deactivate your own administrator account. Users remain responsible for their
own password updates.

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
