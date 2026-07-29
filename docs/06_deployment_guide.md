# CTRL4 Chatbot MK II
## Deployment Guide

Version: MK II Stable (v2.0.0)

---

# Overview

This guide explains how to deploy and run CTRL4 Chatbot MK II in a local development environment.

The chatbot consists of:

- Flask Backend
- HTML/CSS/JavaScript Frontend
- MySQL Database
- AI Engine
- Google Gemini API or Ollama
- Retrieval-Augmented Generation (RAG)

---

# System Requirements

## Software

- Python 3.10 or newer
- MySQL 8.x or MariaDB
- Git
- Visual Studio Code (recommended)

Optional

- Ollama

---

# Clone the Repository

```bash
git clone https://github.com/<your-username>/CTRL4_Chatbot.git

cd CTRL4_Chatbot
```

---

# Create Virtual Environment

```bash
cd backend

python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

macOS / Linux

```bash
source .venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configure Environment Variables

Create

```
backend/.env
```

Example

```env
CHATBOT_DB_HOST=127.0.0.1
CHATBOT_DB_PORT=3306
CHATBOT_DB_USER=root
CHATBOT_DB_PASSWORD=
CHATBOT_DB_NAME=soc_chatbot

CHATBOT_LLM_PROVIDER=gemini

CHATBOT_GEMINI_API_KEY=YOUR_API_KEY
CHATBOT_GEMINI_MODEL=gemini-2.5-flash

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
```

---

# Database Setup

Import the SQL file located in

```
backend/sql/
```

into MySQL.

Ensure the database name matches

```
soc_chatbot
```

or update the `.env` configuration accordingly.

---

# Knowledge Base

Place all Guidance Office documents inside

```
ai_engine/knowledge_base/
```

Then build the RAG index.

Example

```bash
python backend/scripts/ingest_guidance_docs.py
```

---

# Running the Application

Start the backend

```bash
python app.py
```

The server will run on

```
http://127.0.0.1:5000
```

---

# Switching LLM Providers

CTRL4 supports multiple providers.

Gemini

```env
CHATBOT_LLM_PROVIDER=gemini
```

Ollama

```env
CHATBOT_LLM_PROVIDER=ollama
```

No source code changes are required.

---

# Troubleshooting

## Gemini Quota

If the Gemini API returns HTTP 429, the daily free-tier request limit has been reached.

Possible solutions:

- Wait for the quota reset.
- Switch to another Gemini model with available quota.
- Use Ollama locally.
- Upgrade to a paid Gemini plan.

---

## Ollama Not Running

Start Ollama

```bash
ollama serve
```

Verify the selected model has been downloaded

```bash
ollama list
```

---

## Database Connection Issues

Verify:

- MySQL is running
- Database credentials are correct
- Database exists
- Port number matches `.env`

---

## Missing Knowledge Base

If no RAG index is found, rebuild the knowledge base using the ingestion script before starting the application.

---

# Deployment Checklist

Before deployment, verify:

- Python dependencies installed
- Database imported
- Environment variables configured
- Knowledge base indexed
- Gemini or Ollama configured
- Flask server starts successfully
- Student login works
- AI chat responds correctly
- Appointment system functions
- Dashboard loads successfully

---

# Version

CTRL4 Chatbot MK II Stable (v2.0.0)