# CTRL4 English Emotion Model v10 — Runtime Artifact Verification

**Purpose:** operational verification of the exact English emotion-model
artifact used by CTRL4 Chatbot MK III.

## Verification target

The controlled runtime package is located at:

```text
ai_engine/models/english/latest/
```

The package's `runtime_artifact_manifest.json` names the artifact as
`ctrl4-eerm-english-latest-model.safetensors`, version `v10`, and records the
hashes required for release integrity checks.

## Required files

| File | Required SHA-256 |
| --- | --- |
| `model.safetensors` | `d90161c6b064d42ecee866e099f9f3125abb969e7a5ce76cd4c4fb32369ccce9` |
| `config.json` | `d0801564e5d549d6e5aab649e196cdd6e95629e5a1a57c20624acd722165925e` |
| `special_tokens_map.json` | `5d5b662e421ea9fac075174bb0688ee0d9431699900b90662acd44b2a350503a` |
| `tokenizer.json` | `d241a60d5e8f04cc1b2b3e9ef7a4921b27bf526d9f6050ab90f9267a1f9e5c66` |
| `tokenizer_config.json` | `51cde98bb5402e0816faaf75fec5e2c3ade3d290e2c9a72daad76b6f386f3b5e` |
| `vocab.txt` | `07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3` |

## Standard verification procedure

Run this from the repository root after the private production model artifact
has been provisioned:

```bash
.venv/bin/python backend/scripts/verify_emotion_model.py
```

Expected successful result:

```text
English emotion model artifact verification passed.
```

For a manual checksum check:

```bash
shasum -a 256 ai_engine/models/english/latest/model.safetensors \
  ai_engine/models/english/latest/config.json
```

The first two hashes must match the values in the table above. Do not print,
commit, or upload the weight file as part of this process.

## Deployment acceptance criteria

Before treating a deployment as ready, confirm all of the following:

1. The artifact-verification script passes.
2. The application health endpoint reports `emotion_model_loaded: true`.
3. The production health endpoint is reachable through HTTPS.
4. The live model artifact remains outside Git and is readable only by the
   production service account and authorized operators.

## Scope of this record

Integrity verification proves that the expected v10 artifact is present. It
does **not** measure accuracy, F1, bias, clinical suitability, or safety
performance. Those are separate evaluation concerns described in
[v10 Evaluation and Research-Provenance Status](evaluation_status.md).
