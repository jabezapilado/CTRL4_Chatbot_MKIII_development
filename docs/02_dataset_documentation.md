# CTRL4 Chatbot MK II
## 02 — Dataset Documentation

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

CTRL4 Chatbot MK II utilizes multiple datasets to support different artificial intelligence components within the system. Instead of relying on a single dataset, the project combines publicly available Natural Language Processing (NLP) datasets with institution-specific Guidance Office documents to improve both emotion detection and response generation.

The datasets serve two primary purposes:

- Training the emotion detection model.
- Providing verified institutional knowledge through Retrieval-Augmented Generation (RAG).

By combining machine learning datasets with a curated knowledge base, the chatbot generates responses that are both emotionally aware and factually grounded.

---

# Objectives

The dataset collection process was designed to achieve the following objectives:

- Train an emotion detection model using diverse emotional expressions.
- Improve model generalization across different writing styles.
- Reduce dataset bias through dataset integration.
- Standardize emotion labels into a unified taxonomy.
- Build a verified Guidance Office knowledge base.
- Support Retrieval-Augmented Generation (RAG).

---

# Dataset Summary

| Dataset                  | Purpose                      | Samples | Status         |
| ------------------------ | ---------------------------- | ------: | -------------- |
| GoEmotions               | Emotion Detection            |  54,263 | ✅ Integrated  |
| ISEAR                    | Emotion Detection            |   7,102 | ✅ Integrated  |
| DAIR-AI Emotion          | Emotion Detection            |  20,000 | ✅ Integrated  |
| Guidance Office Documents| Knowledge Base (RAG)         |      —  | ✅ Integrated  |
| Empathetic Dialogues     | Research Reference           |  22,933 | 🔄 Optional    |

---

# Emotion Classification Datasets

The following datasets were merged and standardized before training the emotion detection model.

---

## GoEmotions

### Description

GoEmotions is a large-scale emotion classification dataset developed by Google Research. It consists of Reddit comments manually annotated with fine-grained emotion labels.

This dataset serves as the primary source of conversational emotional expressions.

### Purpose

- Primary emotion classification dataset.
- Improves recognition of everyday emotional language.
- Provides diverse conversational patterns.

### Statistics

| Property         | Value                  |
| ---------------- | ---------------------- |
| Source           | Google Research        |
| Samples          | 54,263                 |
| Language         | English                |
| Data Type        | Short Text             |
| Primary Usage    | Emotion Detection      |

---

## ISEAR

### Description

The International Survey on Emotion Antecedents and Reactions (ISEAR) contains written descriptions of personal emotional experiences collected from participants across multiple countries.

Compared to GoEmotions, ISEAR provides longer emotional narratives and more reflective writing styles.

### Purpose

- Improve recognition of personal emotional experiences.
- Increase linguistic diversity.
- Strengthen contextual understanding.

### Statistics

| Property         | Value                  |
| ---------------- | ---------------------- |
| Source           | ISEAR Project          |
| Samples          | 7,102                  |
| Language         | English                |
| Data Type        | Personal Narratives    |
| Primary Usage    | Emotion Detection      |

---

## DAIR-AI Emotion

### Description

The DAIR-AI Emotion dataset contains short sentences labeled with basic emotional categories.

Its clean annotations and balanced sentence structure make it suitable for transformer-based fine-tuning.

### Purpose

- Increase dataset diversity.
- Improve model generalization.
- Supplement existing emotional categories.

### Statistics

| Property         | Value                  |
| ---------------- | ---------------------- |
| Source           | DAIR-AI                |
| Samples          | 20,000                 |
| Language         | English                |
| Data Type        | Short Text             |
| Primary Usage    | Emotion Detection      |

---

# Guidance Office Knowledge Base

Unlike the previous datasets, the Guidance Office Knowledge Base is not used to train machine learning models.

Instead, it supports Retrieval-Augmented Generation (RAG) by supplying verified institutional information during chatbot conversations.

The knowledge base currently contains information related to:

- Guidance Office services
- Office hours
- Counseling procedures
- Appointment information
- Referral guidelines
- Frequently Asked Questions
- Policies and announcements

Whenever a student asks about official Guidance Office information, the chatbot retrieves relevant documents before generating a response.

This significantly reduces hallucinations and improves factual accuracy.

---

# Empathetic Dialogues

The Empathetic Dialogues dataset contains emotionally supportive human-to-human conversations.

Although it is not directly used for emotion classification, it serves as a valuable research reference for designing empathetic conversational behavior and prompt engineering strategies.

Future versions of CTRL4 may integrate this dataset more directly into Retrieval-Augmented Generation or conversational fine-tuning.

---

# Unified Emotion Taxonomy

Since the integrated datasets use different emotion labels, all records were mapped into a common taxonomy before model training.

The current emotion categories are:

- Positive
- Neutral
- Sadness
- Fear
- Anger

Each prediction also includes:

- Overall sentiment
- Confidence score

This standardized taxonomy simplifies training and improves consistency across multiple datasets.

---

# Dataset Integration Workflow

```text
GoEmotions
        │
ISEAR
        │
DAIR-AI Emotion
        │
        ▼
Emotion Label Mapping
        │
        ▼
Schema Standardization
        │
        ▼
Dataset Validation
        │
        ▼
Merged Emotion Dataset
        │
        ▼
DistilBERT Fine-Tuning
        │
        ▼
Emotion Detection Model
```

---

# Knowledge Base Workflow

```text
Guidance Office Documents
            │
            ▼
Document Cleaning
            │
            ▼
Text Chunking
            │
            ▼
Embedding Generation
            │
            ▼
FAISS Index
            │
            ▼
Retrieval-Augmented Generation (RAG)
```

This pipeline prepares institutional documents for efficient semantic retrieval during conversations.

---

# Dataset Storage

```text
ai_engine/

└── data/
    ├── external/
    ├── processed/
    ├── merged/
    └── rag_index/

knowledge_base/
```

The directory structure separates original datasets, processed datasets, merged datasets, and the semantic search index used by the RAG system.

---

# Limitations

The current datasets present several limitations.

- Most emotion datasets are written in English.
- Counseling-specific conversations remain limited.
- Cultural differences may influence emotional expression.
- Institutional knowledge depends on the availability of updated Guidance Office documents.

These limitations will be addressed through additional multilingual datasets and expanded institutional knowledge sources.

---

# Future Improvements

Future dataset enhancements include:

- Filipino emotion datasets
- Tagalog emotion datasets
- Code-switched (English–Filipino) datasets
- Guidance Office conversation datasets
- Student counseling conversation datasets
- Expanded institutional knowledge base
- Additional emotional categories

---

# Summary

CTRL4 Chatbot MK II combines publicly available emotion classification datasets with a curated Guidance Office Knowledge Base to support both machine learning and Retrieval-Augmented Generation.

This hybrid dataset strategy enables the chatbot to recognize emotional context while providing responses grounded in verified institutional information, resulting in a more accurate, supportive, and reliable guidance assistant.