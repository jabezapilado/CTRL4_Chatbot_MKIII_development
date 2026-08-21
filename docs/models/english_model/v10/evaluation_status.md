# CTRL4 English Emotion Model v10 — Evaluation Record

**Status:** Completed reproducible evaluation record
**Evaluation date:** August 21, 2026
**Scope:** English five-class emotion classification only

## Verified artifact and data

The evaluated artifact is the current CTRL4 v10 runtime weight file:

| Item | Verified value |
| --- | --- |
| Artifact version | `v10` |
| Model weight SHA-256 | `d90161c6b064d42ecee866e099f9f3125abb969e7a5ce76cd4c4fb32369ccce9` |
| Test records | 8,047 |
| Test-split fingerprint | `d6240ebcc96abe13` |
| Runtime input limit | 128 tokens |
| Labels | Positive, Neutral, Anger, Sadness, Fear |

The model identity and supporting configuration are documented in the
[Runtime Artifact Verification](runtime_artifact_verification.md).

## Held-out test results

| Metric | Result |
| --- | ---: |
| Accuracy | **80.22%** |
| Weighted precision | **80.14%** |
| Weighted recall | **80.22%** |
| Weighted F1-score | **80.14%** |

| Emotion class | Precision | Recall | F1-score |
| --- | ---: | ---: | ---: |
| Positive | 86.30% | 86.87% | 86.58% |
| Neutral | 73.58% | 75.17% | 74.37% |
| Anger | 73.55% | 66.67% | 69.94% |
| Sadness | 83.27% | 83.83% | 83.55% |
| Fear | 81.58% | 87.45% | 84.42% |

The evaluation was run against the repository's retained English test split,
without retraining or changing its labels. The generated classification report,
confusion matrix, metric files, provenance JSON, and charts are retained only
as protected local research artifacts, not Git content.

## Training-history provenance

The v10 runtime weights exactly match the archived best-model checkpoint
`checkpoint-8092`, selected by validation F1. Its trainer state records the
following available epochs:

| Epoch | Training accuracy | Training loss | Validation accuracy | Validation F1 | Validation loss |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 80.71% | 0.5167 | 77.35% | 77.63% | 0.6203 |
| 2 | 86.11% | 0.3717 | 79.51% | 79.51% | 0.5900 |

The package records five planned training epochs with best-model selection by
validation F1. The archived checkpoint that matches the deployed weight is the
best checkpoint after epoch 2; later archived checkpoint weights are not the
currently deployed v10 model and are not used for this record.

## Reproduction command

Use an approved local copy of the v10 checkpoint history and a clean local
artifact directory:

```bash
.venv/bin/python -m ai_engine.core.training.evaluate_model \
  --artifact-version v10 \
  --output-dir local_artifacts/generated_evaluations/english_model_v10_YYYYMMDD \
  --training-history /path/to/v10/checkpoint-8092/trainer_state.json
```

Before reporting the result, verify that the evaluated `model.safetensors`
hash matches the v10 runtime manifest and preserve the resulting provenance
JSON with the research records.

## Thesis-safe wording

> CTRL4 Chatbot MK III deploys a DistilBERT-based English emotion-classification
> model. In a reproducible evaluation of the verified v10 runtime artifact on
> the retained 8,047-record English test split, it achieved 80.22% accuracy and
> an 80.14% weighted F1-score across Positive, Neutral, Anger, Sadness, and
> Fear classes.

This result is limited to the stated English emotion-classification task. It
does not measure Filipino or Taglish classifier accuracy, clinical diagnosis,
or crisis-detection performance. `SafetyService` and staff review remain the
authoritative safety layers.
