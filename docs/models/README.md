# Model and Evaluation Provenance

This directory preserves thesis research provenance for the English and
Filipino emotion-model work, including historical documentation and tracked
evaluation artifacts. It is not a runtime-artifact distribution channel.

- `english_model/` contains the tracked English model cards, training records,
  and versioned evaluation artifacts.
- `filipino_model/` contains historical Filipino-model planning and evaluation
  documentation.
- `evaluation/` and `training_history.json` are historical tracked outputs.

Model weights, checkpoints, optimizer state, RAG indexes, and generated local
evaluation output are intentionally excluded from ordinary Git history. For
the current runtime model provisioning procedure, use the
[Installation Guide](../deployment/installation_guide.md) and
[Deployment Guide](../deployment/deployment_guide.md).
