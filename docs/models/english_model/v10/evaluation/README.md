# CTRL4 English Emotion Model v10 — Evaluation Assets

**Evaluation date:** August 21, 2026

**Artifact:** Verified CTRL4 English runtime model v10
**Test split:** 8,047 retained English records (`d6240ebcc96abe13`)

This directory contains the thesis-supporting outputs from the reproducible
held-out evaluation documented in the [v10 Evaluation Record](../evaluation_status.md).
It contains documentation artifacts only—no model weights, checkpoints,
optimizer state, student data, or RAG files.

## Result summary

| Metric | Result |
| --- | ---: |
| Accuracy | **80.22%** |
| Weighted precision | **80.14%** |
| Weighted recall | **80.22%** |
| Weighted F1-score | **80.14%** |

## Included files

| File | Purpose |
| --- | --- |
| `overall_metrics.png` | Overall held-out evaluation metrics chart. |
| `per_class_metrics.png` | Precision, recall, and F1 chart for the five output classes. |
| `confusion_matrix.png` | Confusion-matrix chart for the held-out test split. |
| `training_validation_accuracy.png` | Training and validation accuracy history available for the matching best checkpoint. |
| `training_validation_loss.png` | Training and validation loss history available for the matching best checkpoint. |
| `overall_metrics.csv`, `overall_metrics.json` | Machine-readable overall metrics. |
| `per_class_metrics.csv` | Machine-readable per-class metrics. |
| `classification_report.csv` | Full classification-report output. |
| `confusion_matrix.csv` | Machine-readable confusion matrix. |
| `evaluation_provenance.json` | Evaluated artifact, split fingerprint, and generation provenance. |
| `training_history_status.md` | Training-history source and limitations. |

The matching runtime weights are provisioned separately and remain excluded
from Git. See the [Runtime Artifact Verification](../runtime_artifact_verification.md)
for their verified SHA-256 identity.
