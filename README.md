# CTRL4 Chatbot MK III

CTRL4 Chatbot MK III is an undergraduate-thesis Guidance Office support system
for Holy Angel University. It combines authenticated chatbot support,
appointment management, staff case-management workflows, and privacy-preserving
aggregate analytics.

## Current release

The current application uses Flask, MySQL/MariaDB, genuine server-side CacheLib
sessions, and a JavaScript frontend. Its architecture is:

```text
Frontend → Route → Service → Database
```

Students use the chatbot, their own appointments, notifications, and the
approved case-status projection. Guidance staff use authorized appointment,
case-management, settings, analytics, and reporting workflows. Administrators
have account-management-only access at `/admin`; they do not receive Guidance
Office records.

Appointments use current dynamic program-based counselor routing. They store a
start time only, use normalized same-date start-time conflict handling, and
persist active-slot reservations atomically. The canonical appointment statuses
are `pending`, `confirmed`, `cancelled`, `rejected`, and `completed`.

The chatbot supports English, Filipino, and Taglish. Its internal pipeline is
language detection, pre-generation safety, Conversation Intelligence, RAG,
prompt construction, LLM generation, and final response safety validation.
It does not diagnose or prescribe treatment.

## Start here

- [Installation Guide](docs/INSTALLATION_GUIDE.md) — local prerequisites,
  environment configuration, fresh database setup, protected emotion-model and
  RAG provisioning, and the development server.
- [Deployment Guide](docs/06_deployment_guide.md) — authoritative production,
  backup/restore, upgrade, session, logging, and Gunicorn procedure.
- [Project Architecture](docs/01_project_architecture.md) — implemented domain
  boundaries and ownership.
- [API Reference](docs/API_REFERENCE.md) — current endpoint contract.
- [Security, Privacy, RBAC, and Sessions](docs/10_security_architecture.md)
  — implemented controls and deferred work.
- Role guides: [Students](docs/STUDENT_USER_GUIDE.md),
  [Guidance Staff](docs/GUIDANCE_STAFF_USER_GUIDE.md), and
  [Administrators](docs/ADMINISTRATOR_GUIDE.md).
- [Project Context](docs/PROJECT_CONTEXT.md) — frozen decisions through Sprint
  10 and contributor workflow.

The development server listens on `http://127.0.0.1:5001` by default. Do not
commit environment files, credentials, session files, RAG indexes, or real
Guidance Office data.

## Verification

From the repository root, use the documented virtual environment and run the
relevant checks for your change. The baseline repository checks include:

```bash
python3 -m compileall backend/server
python3 -m unittest tests.test_documentation_contracts
python3 -m unittest tests.test_deployment_configuration
python3 -m unittest tests.test_system_integration_contracts
python3 -m unittest tests.test_security_privacy_contracts
git diff --check
```

For database-backed or load testing, use an explicitly configured isolated
database as described in the deployment and test documentation. Never use a
production-like database for integration or mutation tests.

## Historical material

Historical MK II planning, training, roadmap, and model-lineage material is
preserved for thesis provenance. It is not the current implementation contract.
Use the current-reference documents above for development and deployment.
