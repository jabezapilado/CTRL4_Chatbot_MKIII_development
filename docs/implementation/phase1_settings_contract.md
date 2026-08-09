# Phase 1 Settings Contract Audit

This matrix records the pre-implementation audit and Phase 1 action. It does not alter frozen appointment lifecycle, routing, privacy, or safety policy.

| Setting | Persisted source | Service owner | Consumer | Student-safe? | Current UI | Action |
| --- | --- | --- | --- | --- | --- | --- |
| Office name | `officeName` key/value | SettingsService | OperationalGuidanceService | Yes | Live | Seeded when absent or unconfigured |
| Office hours | `officeHours` key/value | SettingsService | OperationalGuidanceService | Yes | Live | Retained as live Office Information |
| Office location | `officeLocation` key/value | SettingsService | OperationalGuidanceService | Yes | Live | Retained as live Office Information |
| Office phone | `contactNumber` key/value | SettingsService | OperationalGuidanceService | Yes | Live | Retained as live Office Information |
| Office email | `officeEmail` key/value | SettingsService | OperationalGuidanceService | Yes | Live | Retained as live Office Information |
| Booking enabled | `appointmentAvailability.bookingEnabled` | SettingsService | AppointmentService, booking projection | Yes | Global Office Settings | Office-wide switch retained as a shared rule |
| Counselor availability | Staff `consultation_schedules` | AccountService | AppointmentService, routed booking projection | No | My Staff Settings | Each counselor manages their own appointment days, times, and rooms; this is the authoritative availability gate |
| Unavailable dates | `appointmentAvailability` exclusions | SettingsService | AppointmentService, booking projection | Yes | Missing | Added as a validated live control |
| Holidays and academic exclusions | `appointmentAvailability` exclusions | SettingsService | AppointmentService | Projected only as unavailable dates | Missing | Preserved in the service contract; no separate unsupported UI source |
| Appointment categories | `appointmentAvailability.appointmentCategories` | SettingsService | AppointmentService, forms | Yes | Static and disconnected | Added as validated live choices |
| Appointment start times | Staff `appointment_slots` | AccountService | AppointmentService, routed booking projection | No | My Staff Settings | Each counselor manages their own selectable start times |
| Consultation modes | Staff `consultation_modes` | AccountService | AppointmentService, routed booking projection | No | My Staff Settings | Each counselor manages their own available modes |
| Appointment duration | None | None | None | N/A | Not shown | Unsupported; no default or UI added |
| Active counselors | Account records | AccountService | Dynamic program routing | No | Admin-managed | Retained outside staff Settings |
| Legacy office windows, start times, and modes | `appointmentAvailability` legacy values | SettingsService | Compatibility only | No | Not editable | Retained for historic records; no longer decides counselor preferences |
| Program routing | Student/staff profile metadata | AppointmentService | Dynamic counselor resolution | No | Not editable | Retained unchanged |
| FAQ records | `faqs` key/value | SettingsService | AIService before RAG/provider output | Yes | Live | Staff-managed, seeded only when absent, and active entries are runtime-consumed |
| Auto-flag | `autoFlag` key/value | None | None | N/A | Disconnected | Removed from Settings UI |
| Supportive message | `showSupport` key/value | None | None | N/A | Disconnected | Removed from Settings UI |
| Escalation message | `escalationMessage` key/value | None | None | N/A | Disconnected | Removed from Settings UI; SafetyService remains frozen |

The student booking projection contains only booking state, unavailable dates, categories, modes, configured start times, and date-specific available slots. It excludes staff identifiers, private schedules, routing assignments, notes, and appointment records.
