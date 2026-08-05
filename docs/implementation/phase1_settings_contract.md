# Phase 1 Settings Contract Audit

This matrix records the pre-implementation audit and Phase 1 action. It does not alter frozen appointment lifecycle, routing, privacy, or safety policy.

| Setting | Persisted source | Service owner | Consumer | Student-safe? | Current UI | Action |
| --- | --- | --- | --- | --- | --- | --- |
| Office hours | `officeHours` key/value | SettingsService | OperationalGuidanceService | Yes | Live | Retained as live Office Information |
| Office location | `officeLocation` key/value | SettingsService | OperationalGuidanceService | Yes | Live | Retained as live Office Information |
| Office phone | `contactNumber` key/value | SettingsService | OperationalGuidanceService | Yes | Live | Retained as live Office Information |
| Office email | `officeEmail` key/value | SettingsService | OperationalGuidanceService | Yes | Live | Retained as live Office Information |
| Booking enabled | `appointmentAvailability.bookingEnabled` | SettingsService | AppointmentService, booking projection | Yes | Missing | Added as a validated live control |
| Weekdays and time ranges | `appointmentAvailability.officeAvailability` | SettingsService | AppointmentService, booking projection | Yes | Missing | Added as structured live controls |
| Unavailable dates | `appointmentAvailability` exclusions | SettingsService | AppointmentService, booking projection | Yes | Missing | Added as a validated live control |
| Holidays and academic exclusions | `appointmentAvailability` exclusions | SettingsService | AppointmentService | Projected only as unavailable dates | Missing | Preserved in the service contract; no separate unsupported UI source |
| Appointment categories | `appointmentAvailability.appointmentCategories` | SettingsService | AppointmentService, forms | Yes | Static and disconnected | Added as validated live choices |
| Consultation modes | `appointmentAvailability.consultationModes` | SettingsService | AppointmentService, forms | Yes | Static and disconnected | Added as validated live choices |
| Appointment duration | None | None | None | N/A | Not shown | Unsupported; no default or UI added |
| Active counselors | Account records | AccountService | Dynamic program routing | No | Admin-managed | Retained outside staff Settings |
| Counselor consultation schedules | Staff profile metadata | AccountService | AppointmentService | No | Admin-managed | Retained outside staff Settings |
| Program routing | Student/staff profile metadata | AppointmentService | Dynamic counselor resolution | No | Not editable | Retained unchanged |
| FAQ records | `faqs` key/value | None | None | N/A | Disconnected | Removed from Settings UI |
| Auto-flag | `autoFlag` key/value | None | None | N/A | Disconnected | Removed from Settings UI |
| Supportive message | `showSupport` key/value | None | None | N/A | Disconnected | Removed from Settings UI |
| Escalation message | `escalationMessage` key/value | None | None | N/A | Disconnected | Removed from Settings UI; SafetyService remains frozen |

The student booking projection contains only booking state, office windows, unavailable dates, categories, and consultation modes. It excludes staff identifiers, private schedules, routing assignments, notes, and appointment records.