# CTRL4 English Emotion Recognition Model — Runtime Release v10

**Status:** Runtime model card and integrity record
**Artifact version:** v10
**System role:** English emotion-inference component for CTRL4 Chatbot MK III
**Last verified:** August 21, 2026

## 1. Purpose and scope

This document describes the approved **v10 runtime artifact** currently loaded
by CTRL4 from `ai_engine/models/english/latest`. It identifies what is
technically verifiable from the deployed model package and its accompanying
manifest. It is not a clinical diagnostic instrument and it does not make the
final safety decision for a student.

The model contributes emotion information to the chatbot's broader AI flow:

```text
Language detection → SafetyService → Conversation Intelligence → RAG
→ PromptBuilder → LLM → ResponseSafetyService
```

`SafetyService` remains authoritative for pre-generation crisis and escalation
decisions. The classifier's output is one input to the system; it must not be
used alone to diagnose depression, abuse, self-harm risk, or any mental-health
condition.

## 2. Verified runtime identity

| Property | Verified value |
| --- | --- |
| Manifest | `ai_engine/models/english/latest/runtime_artifact_manifest.json` |
| Artifact name | `ctrl4-eerm-english-latest-model.safetensors` |
| Artifact version | `v10` |
| Model weight file | `ai_engine/models/english/latest/model.safetensors` |
| Weight size | 267,841,796 bytes |
| Weight SHA-256 | `d90161c6b064d42ecee866e099f9f3125abb969e7a5ce76cd4c4fb32369ccce9` |
| Configuration SHA-256 | `d0801564e5d549d6e5aab649e196cdd6e95629e5a1a57c20624acd722165925e` |

The runtime manifest should be checked before a production deployment. Model
weights are provisioned separately from Git and must remain outside ordinary
repository history.

## 3. Architecture and inference configuration

| Property | Value |
| --- | --- |
| Architecture | `DistilBertForSequenceClassification` |
| Base architecture | DistilBERT (`distilbert-base-uncased` configuration) |
| Task type | Single-label sequence classification |
| Number of output labels | 5 |
| Transformer layers | 6 |
| Attention heads | 12 |
| Hidden dimension | 768 |
| Vocabulary size | 30,522 |
| Runtime input limit | 128 tokens in CTRL4 emotion-classifier preprocessing |
| Maximum model position embeddings | 512 |

The model package records the following training arguments: learning rate
`1.8e-5`, training/evaluation batch size `16`, five planned epochs, weight
decay `0.01`, warm-up ratio `0.1`, random seed `42`, and best-model selection
using validation F1. The deployed v10 weights match archived best checkpoint
`checkpoint-8092`, whose trainer history records the available epoch-one and
epoch-two validation results.

## 4. Output taxonomy

CTRL4 resolves the model's numeric output through
`ai_engine/configs/label_encoder.json`.

| Label ID | Emotion class | High-level sentiment grouping |
| ---: | --- | --- |
| 0 | Positive | Positive |
| 1 | Neutral | Neutral |
| 2 | Anger | Negative |
| 3 | Sadness | Negative |
| 4 | Fear | Negative |

These are the classifier's direct output classes. Concepts such as anxiety,
hopelessness, abuse, diagnosis-related language, and warning signs are handled
by higher-level safety and conversation services; they are not additional
emotion labels produced by this classifier.

## 5. Language boundary

The v10 transformer is an **English emotion model**. CTRL4 supports English,
Filipino, and Taglish at the system level through language detection, safety
rules, retrieval, prompt construction, and the conversational LLM. However,
the repository does not claim a separately trained Filipino or Tagalog
transformer emotion-classification model.

## 6. Responsible use and limitations

- The model provides a probabilistic emotion classification for an input text;
  it is not a mental-health diagnosis or a replacement for a counselor.
- Safety handling is intentionally conservative. Explicit crisis, self-harm,
  harm-to-others, abuse, warning-sign, and self-diagnosis language is evaluated
  by `SafetyService` before normal response generation.
- Generated text is validated by `ResponseSafetyService`; unsafe generated
  output is replaced rather than exposed to the student.
- Staff see privacy-safe summaries and authorized case information, not a
  classifier result as a standalone clinical conclusion.

## 7. Evaluation provenance

A reproducible held-out evaluation of the verified v10 runtime artifact on the
retained 8,047-record English test split recorded **80.22% accuracy** and an
**80.14% weighted F1-score**. The complete result, per-class metrics,
test-split fingerprint, and training-history provenance are in
[v10 Evaluation Record](evaluation_status.md).

The historical v1 metrics in [`../v1/evaluation.md`](../v1/evaluation.md) still
belong to **v1/MK II** and must retain that version label in the thesis.
