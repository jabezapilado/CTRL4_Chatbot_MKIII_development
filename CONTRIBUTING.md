# Contributing to CTRL4 Chatbot MK III

Thank you for helping improve **CTRL4 Chatbot MK III**, an undergraduate thesis
project for the School of Computing Guidance Office at Holy Angel University.
The system handles student-support workflows and potentially sensitive content.
Contributions must therefore protect privacy, preserve Guidance Office workflow
boundaries, and remain appropriate for an academic project.

## Project contribution record

The project documents the following primary contribution areas across the
CTRL4 prototype iterations:

- **Jabez Timothy Apilado:** primary system development, system integration,
  and the completed MK III implementation.
- **Teyshaun Zell R. Wylengco:** UI/UX design.
- **Grant Mihkael Quilantang:** frontend development for MK I and MK II.
- **Lanix T. Iligan:** public emotion-dataset sourcing and legacy AI-engine
  development.

This record is attribution, not a reassignment of repository ownership,
maintainer authority, security contacts, or approval responsibilities.

## Before contributing

- Read the [README](README.md), the [documentation index](docs/README.md), and
  the relevant guide or architecture reference before changing a feature.
- Report security, privacy, access-control, or safety concerns privately under
  the process in [SECURITY.md](SECURITY.md); do not open a public issue that
  contains sensitive details.
- Do not submit student information, credentials, API keys, `.env` files, SQL
  backups, model weights, generated RAG artifacts, screenshots containing
  protected data, deferred patches, or local evaluation materials.
- Treat the current implementation and approved Guidance Office procedures as
  authoritative. Archived roadmaps are context, not permission to revive an
  unfinished feature.

## Contribution scope

Appropriate contributions include focused bug fixes, accessibility and
responsive-interface improvements, tests, documentation corrections, approved
Guidance Office knowledge-base updates, and maintainable changes to existing
workflows. New features that change data collection, notifications, emergency
handling, external integrations, access roles, or appointment rules need prior
approval from the project maintainers and, where applicable, the Guidance
Office.

CTRL4 is not a clinical diagnosis, therapy, or emergency-response system. Do
not change safety copy, crisis handling, warning-sign behavior, or escalation
rules without an approved safety review.

## Development expectations

Keep changes small and focused. Preserve the existing architecture:

```text
Route → Service → Database
```

- Routes own HTTP parsing, role checks, session lifecycle, and API responses.
- Services own workflow rules, authorization, privacy projections, and AI
  orchestration.
- Database helpers own parameterized persistence only.

Preserve server-side Flask sessions, CSRF protection, Terms gating,
student-ownership checks, program-scoped staff access, and the canonical roles
`student`, `staff`, and `admin`. Administrators do not receive Guidance Office
case, appointment, or conversation authority.

The required AI processing order is:

```text
Language detection → SafetyService → Conversation Intelligence → RAG
→ PromptBuilder → LLM → ResponseSafetyService
```

`SafetyService` remains the pre-generation authority for safety assessment and
staff escalation. The emotion classifier is an English emotional-context
signal, not a clinical diagnosis or the sole basis for an escalation decision.

## Suggested local workflow

1. Create a focused branch from the current `main` branch.
2. Make the smallest maintainable change and add or update focused tests.
3. Update documentation whenever behavior, UI, operations, deployment,
   configuration, privacy, or security is affected.
4. Run the relevant checks from the repository root:

   ```bash
   python3 -m compileall backend/server
   git diff --check
   ```

   Also run `node --check` for every changed frontend JavaScript file and the
   focused Python tests for the changed behavior.
5. Clearly describe the change, validation performed, and any known limits in
   the pull request or review request.

## Production and deployment

Production runs on the Contabo VPS behind Nginx and systemd. A reviewed push to
`main` triggers the repository's GitHub Actions deployment workflow. Do not
make direct untracked production code edits, commit production secrets, or
replace the provisioned MySQL data, RAG index, HTTPS configuration, or uploaded
emotion-model artifact. Follow the [Deployment Guide](docs/deployment/deployment_guide.md)
for the approved setup, verification, and recovery process.

## Attribution

Contributions are subject to the [Academic Use License](LICENSE). Preserve the
original author notices and do not represent this thesis project as your own
work. The maintainers may decline changes that exceed the approved thesis scope
or conflict with privacy, safety, or Guidance Office requirements.
