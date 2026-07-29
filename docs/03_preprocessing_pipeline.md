# CTRL4 Chatbot MK II
## 03 — Preprocessing Pipeline

**Version:** MK II Stable (v2.0.0)

**Authors**

- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell

**Capstone Project**

Development of an AI-Powered Guidance Chatbot for Inquiry Management Using NLP-Based Negative Emotion Detection

**Institution**

Holy Angel University

**Program**

Bachelor of Science in Computer Science

**Academic Year**

2026–2027

**Last Updated**

July 2026

---

# Overview

Before datasets and institutional documents can be used by the AI components of CTRL4 Chatbot MK II, they undergo preprocessing to ensure consistency, quality, and compatibility.

The preprocessing pipeline consists of two independent workflows:

- **Emotion Dataset Preprocessing**, which prepares multiple public emotion datasets for DistilBERT training.
- **Knowledge Base Preprocessing**, which prepares Guidance Office documents for Retrieval-Augmented Generation (RAG).

Separating these workflows allows the system to maintain a clear distinction between machine learning datasets and institutional knowledge while ensuring that both components remain scalable and maintainable.

---

# Objectives

The preprocessing pipeline was designed to achieve the following objectives:

- Standardize multiple emotion datasets into a common structure.
- Normalize emotion labels across different datasets.
- Remove invalid or incomplete records.
- Produce a unified dataset for transformer-based emotion classification.
- Prepare Guidance Office documents for semantic retrieval.
- Ensure reproducible preprocessing for future development.

---

# Overall Preprocessing Pipeline

```text
                External Resources
                ┌─────────┴─────────┐
                │                   │
                ▼                   ▼
      Emotion Datasets      Guidance Documents
                │                   │
                ▼                   ▼
       Dataset Cleaning     Document Cleaning
                │                   │
                ▼                   ▼
       Label Mapping         Text Chunking
                │                   │
                ▼                   ▼
      Schema Validation     Embedding Generation
                │                   │
                ▼                   ▼
      Merged Dataset          FAISS Index
                │                   │
                ▼                   ▼
     Emotion Detection        RAG Retrieval
```

The preprocessing pipeline prepares both machine learning datasets and institutional documents for their respective AI components.

---

# Emotion Dataset Preprocessing

The emotion preprocessing pipeline converts multiple public datasets into a unified training dataset.

Supported datasets include:

- GoEmotions
- ISEAR
- DAIR-AI Emotion

Each dataset follows the same preprocessing workflow regardless of its original structure.

---

## Dataset Loading

Datasets are loaded from the `ai_engine/data/external` directory.

Each dataset is validated before preprocessing begins.

---

## Text Cleaning

Basic text normalization is applied to every record.

Cleaning operations include:

- Removing leading and trailing whitespace
- Removing empty records
- Collapsing multiple spaces
- Normalizing text formatting

These operations ensure consistent textual input for transformer tokenization.

---

## Record Validation

Every record is validated before inclusion in the processed dataset.

Validation rules include:

- Text must exist.
- Text must not be empty.
- Required fields must be present.
- Invalid records are discarded.

---

## Emotion Mapping

Each dataset uses different emotion labels.

All labels are mapped into a standardized taxonomy.

| Original Label | Standardized Emotion |
| -------------- | -------------------- |
| Joy            | Positive             |
| Love           | Positive             |
| Surprise       | Positive             |
| Neutral        | Neutral              |
| Anger          | Anger                |
| Sadness        | Sadness              |
| Fear           | Fear                 |

This standardization allows multiple datasets to be merged without conflicts.

---

## Sentiment Mapping

Each standardized emotion is mapped to a broader sentiment category.

| Emotion  | Sentiment | Negative Emotion |
| -------- | --------- | ---------------- |
| Positive | Positive  | No               |
| Neutral  | Neutral   | No               |
| Anger    | Negative  | Yes              |
| Sadness  | Negative  | Yes              |
| Fear     | Negative  | Yes              |

This metadata is later used by the emotion detection model and chatbot safety logic.

---

## Schema Standardization

Every processed record follows a common schema.

| Field              | Description                    |
| ------------------ | ------------------------------ |
| id                 | Unique record identifier       |
| text               | Cleaned student text           |
| original_emotion   | Original dataset label         |
| emotion            | Standardized emotion           |
| sentiment          | Standardized sentiment         |
| is_negative        | Negative emotion flag          |
| source             | Dataset source                 |

The standardized schema ensures consistency during model training.

---

## Dataset Merging

After preprocessing, all processed datasets are merged into a single dataset.

The merge process performs:

- Dataset loading
- Dataset concatenation
- Duplicate removal
- Record shuffling
- Split preservation
- Dataset export

The resulting dataset becomes the training input for the DistilBERT emotion classifier.

---

# Knowledge Base Preprocessing

Unlike emotion datasets, Guidance Office documents are prepared for Retrieval-Augmented Generation rather than model training.

The preprocessing pipeline consists of the following stages.

---

## Document Collection

Official Guidance Office documents are collected from approved institutional sources.

Typical documents include:

- Office hours
- Counseling services
- Appointment procedures
- Policies
- Frequently Asked Questions
- Referral guidelines

---

## Document Cleaning

Documents are cleaned before indexing.

Cleaning operations include:

- Removing unnecessary formatting
- Removing empty sections
- Normalizing whitespace
- Standardizing document structure

---

## Text Chunking

Large documents are divided into smaller overlapping text chunks.

Chunking improves retrieval accuracy by allowing the semantic search engine to retrieve only the most relevant sections instead of entire documents.

---

## Embedding Generation

Each text chunk is converted into a dense vector representation using a multilingual sentence embedding model.

These embeddings capture semantic meaning rather than exact keyword matches.

---

## FAISS Index Creation

Generated embeddings are stored inside a FAISS vector index.

The index enables efficient semantic similarity searches during chatbot conversations.

---

# Directory Structure

```text
ai_engine/

├── configs/
├── core/
├── data/
│   ├── external/
│   ├── processed/
│   ├── merged/
│   └── rag_index/
│
├── knowledge_base/
└── models/
```

The directory structure separates raw datasets, processed datasets, merged datasets, vector indexes, and institutional knowledge.

---

# Advantages of the Pipeline

The preprocessing pipeline provides several benefits.

- Standardizes multiple public datasets.
- Produces reproducible preprocessing results.
- Supports modular AI development.
- Separates model training from knowledge retrieval.
- Improves semantic search accuracy.
- Reduces hallucinations through verified institutional documents.

---

# Current Limitations

The current preprocessing pipeline has several limitations.

- Most emotion datasets are English-only.
- No automatic spelling correction.
- Limited slang normalization.
- Limited multilingual preprocessing.
- Institutional knowledge depends on manually curated documents.

---

# Future Improvements

Future preprocessing enhancements include:

- Filipino preprocessing
- Tagalog preprocessing
- Code-switched preprocessing
- Emoji normalization
- Internet slang normalization
- Automatic duplicate detection
- Knowledge base versioning
- Automated document ingestion

---

# Summary

The preprocessing pipeline of CTRL4 Chatbot MK II prepares both machine learning datasets and institutional knowledge for artificial intelligence components.

Emotion datasets are standardized and merged to support DistilBERT emotion classification, while Guidance Office documents are cleaned, chunked, embedded, and indexed to support Retrieval-Augmented Generation. Together, these preprocessing workflows provide the foundation for accurate emotion recognition and reliable, context-aware responses grounded in verified institutional information.