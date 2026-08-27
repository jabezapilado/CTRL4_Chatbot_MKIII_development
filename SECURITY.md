# Security Policy

CTRL4 Chatbot MK III handles student-support workflows and may process sensitive
emotional or safety-related messages. Security, privacy, and the correct
handling of escalated cases are therefore core project requirements.

## Supported version

| Version | Supported | Notes |
| --- | --- | --- |
| Current `main` / `v1.0.x` | Yes | Active thesis and production-maintenance line. |
| Earlier prototype releases | No | Historical research artifacts; do not deploy them. |

## Security and privacy controls

The implementation currently includes the following boundaries:

- Flask server-side sessions with an opaque browser session identifier;
  production cookies use `Secure`, `HttpOnly`, and `SameSite=Lax` controls.
- Server-side authentication and role authorization for exactly `student`,
  `staff`, and `admin` roles. Staff visibility is program-scoped, and
  administrators do not have Guidance Office case, appointment, or
  conversation authority.
- Student ownership checks, explicit student Terms acceptance before chat
  access, and CSRF protection for authenticated state-changing requests.
- Parameterized database access and integrity safeguards for MySQL/MariaDB
  persistence.
- Temporary raw chat handling with privacy-safe staff review projections;
  protected raw messages, prompts, blocked outputs, credentials, and private
  counselor notes must not be written to routine application logs.
- Production configuration and secrets stored only on the VPS in `backend/.env`;
  repository deployment uses GitHub Actions and does not commit those values.
- HTTPS termination through the production Nginx configuration.

The authoritative implementation detail is maintained in
[Security Architecture](docs/architecture/security_architecture.md). This
policy summarizes existing controls and does not claim features that are only
future recommendations.

## AI safety boundary

CTRL4 is a Guidance Office support tool, not an emergency service, clinical
diagnosis tool, or replacement for professional judgment. Its required AI flow
uses `SafetyService` before generation and `ResponseSafetyService` after
generation. `SafetyService` is authoritative for crisis and escalation
assessment; the English emotion model contributes emotional context only.
Authorized Guidance Office personnel remain responsible for reviewing pending
warning signs, abuse disclosures, and escalated concerns.

## Reporting a vulnerability

**Do not post a public issue** for a possible privacy leak, account-access
issue, CSRF/session weakness, exposed secret, unauthorized case access, or
unsafe AI behavior involving real or identifiable student content.

Report it privately through the repository's GitHub Security Advisories. If
that channel is unavailable, contact the project maintainers using a private
university or repository-owner contact channel. Do not include live passwords,
tokens, complete student messages, screenshots with identifiable data, or other
protected data in the initial report.

Please include:

- A concise description and potential impact.
- Safe steps to reproduce, ideally using test data.
- The affected route, component, browser, device, or deployment context.
- Any suggested mitigation or workaround.

## Response approach

The maintainers will acknowledge and triage reports in good faith within the
constraints of the undergraduate thesis project. Confirmed fixes are reviewed,
tested, documented when needed, and released through the tracked production
deployment workflow. Public disclosure should wait until the affected issue has
been assessed and a safe disclosure plan is agreed.

## Security acknowledgments

Verified, responsibly disclosed issues may be acknowledged in release notes at
the discretion of the project maintainers and only with the reporter's consent.
