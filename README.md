# CTRL4 Chatbot MK III

> **Development of an AI-Powered Guidance Chatbot for Inquiry Management Using
> NLP-Based Negative Emotion Detection**

[![Release](https://img.shields.io/badge/release-v1.0.0-2f6feb)](https://github.com/jabezapilado/CTRL4_Chatbot_MKIII/releases/tag/v1.0.0)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)
![Database](https://img.shields.io/badge/database-MySQL%20%7C%20MariaDB-4479A1)
![License](https://img.shields.io/badge/license-Academic%20Use-6f42c1)

## Overview

CTRL4 Chatbot MK III is an undergraduate-thesis Guidance Office support system
for Holy Angel University. It combines authenticated chatbot support,
appointment management, staff case-management workflows, and
privacy-preserving aggregate analytics.

The application uses a JavaScript frontend, Flask, MySQL/MariaDB, and genuine
server-side CacheLib sessions. Its implementation follows:

```text
Frontend → Route → Service → Database
```

## Project status

**Current stable release:** [v1.0.0](https://github.com/jabezapilado/CTRL4_Chatbot_MKIII/releases/tag/v1.0.0)

MK III is the completed, current implementation. Historical roadmaps and MK II
research records remain available for thesis provenance, but they are not the
current system contract.

## Features

### AI and chatbot

- English, Filipino, and Taglish interaction at the response/rule level.
- Language Detection, SafetyService, internal intent/emotion/topic/metadata
  processing, RAG, PromptBuilder, and ResponseSafetyService.
- Gemini and Ollama provider support through the existing provider abstraction.
- Guidance Office knowledge retrieval from approved records.
- An externally provisioned English emotion-model artifact; model weights are
  intentionally not stored in ordinary Git history.

The released emotion model is English-focused. Filipino/Tagalog and Taglish
language detection and response rules are implemented, but their emotion
classification should not be treated as equivalent to a separately validated
Filipino or Taglish emotion model.

### Student workflows

- Authenticated chatbot use after accepting the per-session Terms and
  Conditions acknowledgement.
- Appointment booking, history, cancellation, and replacement rescheduling.
- Recipient-scoped in-app notifications.
- Privacy-projected personal case-status view.

### Guidance-staff workflows

- Dynamically program-routed appointment management and manual appointments.
- Appointment lifecycle, counselor notes, and read-only calendar.
- Flagged-case review, case notes, referrals, interventions, and
  confidentiality handling.
- Summary-based Inbox, active Flagged Cases, privacy-safe Case Details
  (including separate Detected Emotion and Safety Risk), and Reviewed Case
  History.
- Read-only appointment, chatbot, counselor-workload, and flagged-case
  analytics, plus aggregate-only CSV reports.

### Administrator workflow

- Account management only. Administrators do not receive Guidance Office
  appointments, conversations, case records, notes, analytics, or reports.

## What’s new in MK III

MK III extends the earlier modular chatbot baseline with appointment operations,
dynamic counselor routing, persistent notifications, case management,
privacy-projected student case status, aggregate analytics, CSV reporting,
server-side sessions, release-readiness testing, and deployment documentation.

## Architecture

The chatbot pipeline preserves the following order:

```text
Language Detection
→ SafetyService
→ Conversation Intelligence
→ RAG
→ PromptBuilder
→ LLM generation
→ ResponseSafetyService
→ response/finalization/escalation handling
```

SafetyService remains authoritative for pre-generation crisis and diagnosis
handling. The chatbot does not diagnose, prescribe treatment, or expose hidden
prompts, internal summaries, or protected case data.

For complete ownership, privacy, session, and API details, use the
[documentation index](docs/README.md).

## Technology stack

- **Backend:** Python, Flask, Flask-Session/CacheLib
- **Database:** MySQL or MariaDB
- **AI and retrieval:** PyTorch, Transformers, Sentence Transformers, FAISS,
  Gemini or Ollama
- **Frontend:** HTML, CSS, and JavaScript

## Requirements

- Python 3.10 or newer
- MySQL 8.x or MariaDB
- Git
- Either a configured Gemini provider or a reachable Ollama provider
- Approved Guidance Office knowledge records and the externally provisioned
  English emotion-model artifact

## Quick installation

Use this concise development path; the linked guides remain authoritative for
database upgrade, backup/restore, model provisioning, and production setup.

```bash
git clone https://github.com/jabezapilado/CTRL4_Chatbot_MKIII.git
cd CTRL4_Chatbot_MKIII

python3 -m venv backend/.venv
./backend/.venv/bin/python -m pip install --upgrade pip
./backend/.venv/bin/python -m pip install -r requirements.txt

cp backend/.env.example backend/.env
# Configure backend/.env without committing it.
```

Then prepare a fresh database or follow the backup-first upgrade procedure,
provision the runtime model artifact, build the approved RAG index, and start
the application:

```bash
./backend/.venv/bin/python backend/scripts/verify_emotion_model.py
cd backend
../.venv/bin/python scripts/ingest_guidance_docs.py
../.venv/bin/python app.py
```

By default, the development server listens at
`http://127.0.0.1:5001`. Verify it with:

```bash
curl --fail --silent --show-error http://127.0.0.1:5001/health
```

For a temporary Tailscale or local-network demonstration only, start with
`CTRL4_HOST=0.0.0.0`. This is opt-in; it is not the default binding. Use
`CTRL4_PORT` to override port `5001` when needed.

## MK III operational notes

- The validated local XAMPP MariaDB database is `soc_chatbot`. The MK III audit
  found `db.py`, `backend/sql/schema.sql`, and the live schema structurally
  aligned. Demo chat/case test records were cleaned after a verified SQL backup;
  foundation accounts, settings, program catalog, FAQs, appointment
  availability, and staff profiles remain preserved.
- Versioned database migrations and the audit's nine candidate indexes are
  deferred. The saved `mkiii_startup_hardening_unvalidated.patch` is not part
  of the release and must not be applied as a validated feature.
- Generated RAG artifacts require deliberate review and handling; do not treat
  them as ordinary disposable build output.
- This thesis/demo system has meaningful access, privacy, and request controls,
  but it is not represented as fully production-hardened.

## LLM provider configuration

Configure provider values only in `backend/.env`:

- Use the configured Gemini variables when `CHATBOT_LLM_PROVIDER=gemini`.
- Use the configured Ollama URL and model values when
  `CHATBOT_LLM_PROVIDER=ollama`.

Do not place API keys, cookies, database credentials, or production endpoints
in source files or documentation. See the
[Installation Guide](docs/deployment/installation_guide.md) and
[Deployment Guide](docs/deployment/deployment_guide.md) for the supported
environment configuration and single-instance deployment topology.

## Project structure

```text
ai_engine/          AI runtime, knowledge records, and training utilities
backend/            Flask application, services, database helpers, and scripts
docs/               Current references, guides, research provenance, and history
frontend/           Templates and safe client-side presentation
tests/              Contract, integration, privacy, and release-readiness tests
```

## Documentation

- [Documentation index](docs/README.md)
- [Installation Guide](docs/deployment/installation_guide.md)
- [Deployment Guide](docs/deployment/deployment_guide.md)
- [Project Architecture](docs/architecture/project_architecture.md)
- [Security Architecture](docs/architecture/security_architecture.md)
- [API Reference](docs/architecture/api_reference.md)
- [Student Guide](docs/guides/student_guide.md)
- [Guidance Staff Guide](docs/guides/guidance_staff_guide.md)
- [Administrator Guide](docs/guides/administrator_guide.md)
- [Project Context](docs/architecture/project_context.md)
- [Changelog](CHANGELOG.md)

## Screenshots

No approved, sanitized release screenshots are currently included. Do not add
screenshots containing student identifiers, appointments, conversations, case
records, notes, credentials, or other protected data.

## Version history

- **MK I:** Initial prototype.
- **MK II:** Modular AI redesign and architecture baseline.
- **MK III:** Current completed system with appointments, case management,
  analytics, security/privacy controls, deployment preparation, documentation,
  and release-readiness verification.

For the complete history, see [CHANGELOG.md](CHANGELOG.md).

## Contributors

Project authors and the academic-use terms are recorded in [LICENSE](LICENSE).
Do not remove or alter original authorship notices.

## License

This repository is provided under the [Academic Use License](LICENSE).
