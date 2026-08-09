# CTRL4 Chatbot MK III — Installation Guide

> For production, database upgrades, backup/restore, and Gunicorn deployment,
> use the authoritative [Deployment Guide](deployment_guide.md). This guide
> is the concise local-installation path.

## Prerequisites

- Python 3.10 or newer
- MySQL 8.x or MariaDB
- Git
- A configured Gemini provider or reachable Ollama instance
- Guidance knowledge records, a validated RAG index directory, and the
  protected English emotion-model release artifact

## Install dependencies

The root [`requirements.txt`](../../requirements.txt) is the canonical dependency
manifest.

```bash
python3 -m venv backend/.venv
./backend/.venv/bin/python -m pip install --upgrade pip
./backend/.venv/bin/python -m pip install -r requirements.txt
```

## Configure the environment

```bash
cp backend/.env.example backend/.env
chmod 600 backend/.env
```

Configure database, session, logging, LLM, and RAG values in `backend/.env`.
Development defaults to `http://127.0.0.1:5001`. Do not commit `.env` or place
credentials in documentation.

## Prepare a database

For a new empty development database, create the database and load
`backend/sql/schema.sql`; see the exact commands in the
[Deployment Guide](deployment_guide.md#database-initialization). The validated
MK III local database is XAMPP MariaDB `soc_chatbot`; its live schema aligned
with both `db.py` and `schema.sql`. Do not run migrations or cleanup against an
existing database without a separate approved plan and verified backup.

## Provision AI runtime assets

### English emotion model

The English emotion-model weight is intentionally not stored in ordinary Git.
Obtain the approved controlled release artifact
`ctrl4-eerm-english-latest-model.safetensors` from the project release
custodian and copy it to:

```text
ai_engine/models/english/latest/model.safetensors
```

It must be exactly `267841796` bytes and have SHA-256:

```text
d90161c6b064d42ecee866e099f9f3125abb969e7a5ce76cd4c4fb32369ccce9
```

Verify the complete minimum runtime artifact before startup:

```bash
./backend/.venv/bin/python backend/scripts/verify_emotion_model.py
```

Startup fails clearly if the model artifact is missing. The application does
not substitute an unrelated model.

### RAG index and start development

Build the knowledge index from the approved current knowledge records after
configuring the RAG directories:

```bash
cd backend
../.venv/bin/python scripts/ingest_guidance_docs.py
../.venv/bin/python app.py
```

The default listener is `127.0.0.1:5001`. For a temporary private Tailscale
demo, no code or `.env` edit is necessary. In the terminal that starts Flask:

```bash
export CTRL4_HOST="$(tailscale ip -4)"
export CTRL4_PORT=5001
../.venv/bin/python app.py
```

Share the value from `tailscale ip -4` only with permitted devices in the same
tailnet, using `http://TAILSCALE_IP:5001`. `CTRL4_HOST=0.0.0.0` is available
only when a LAN demonstration genuinely requires it; it is broader because it
also listens on LAN interfaces. Do not use Tailscale Funnel or public port
forwarding. Stop with `Ctrl+C` and run `unset CTRL4_HOST CTRL4_PORT` before a
normal start in that terminal.

The generated manifest records a deterministic fingerprint of the configured
source set and RAG settings. At startup, a mismatched index is rebuilt only
when `CHATBOT_RAG_AUTO_BUILD_ON_START=true`; otherwise it is reported as stale
and is not used.

Verify startup without sending protected content:

```bash
curl --fail --silent --show-error http://127.0.0.1:5001/health
```

For production Gunicorn startup, explicit upgrade/backup procedure, and log
locations, follow the [Deployment Guide](deployment_guide.md) rather than
duplicating those operational steps here.
