# Model and Evaluation Provenance

This directory preserves thesis research provenance for the English and
Filipino emotion-model work, including historical documentation and tracked
evaluation artifacts. It is not a runtime-artifact distribution channel.

- `english_model/` contains the tracked English model cards, training records,
  versioned evaluation artifacts, and the verified current-runtime v10
  documentation set:
  - [`english_model/v10/model_card.md`](english_model/v10/model_card.md)
  - [`english_model/v10/runtime_artifact_verification.md`](english_model/v10/runtime_artifact_verification.md)
  - [`english_model/v10/evaluation_status.md`](english_model/v10/evaluation_status.md)
  - [`english_model/v10/evaluation/`](english_model/v10/evaluation/) for the
    versioned v10 charts, metrics, and evaluation provenance.
- `filipino_model/` contains historical Filipino-model planning and evaluation
  documentation.
- `evaluation/` and `training_history.json` are historical tracked outputs.

Model weights, checkpoints, optimizer state, RAG indexes, and generated local
evaluation output are intentionally excluded from ordinary Git history. For
the current runtime model provisioning procedure, use the
[Installation Guide](../deployment/installation_guide.md) and
[Deployment Guide](../deployment/deployment_guide.md).

## Runtime release retention

The live CTRL4 application loads only the approved English release at
`ai_engine/models/english/latest`. Its small tokenizer and configuration files
are retained with the source code so the controlled weight artifact can be
verified at deployment time. The weight itself is provisioned separately.

Earlier local releases, optimizer state, and `checkpoint-*` training folders
are archival material. Keep them outside the repository in protected local or
institutional storage; do not add them back to Git or treat them as deployment
dependencies.

The v10 runtime manifest verifies artifact identity and integrity. Its matching
held-out evaluation record is available in
[`english_model/v10/evaluation_status.md`](english_model/v10/evaluation_status.md).
Historical version metrics must still retain their original version and
evaluation context.
