# English Emotion Recognition Model (EERM)

**Version:** 1.0 (MK II)

---

# Authors

- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell

---

# Overview

The English Emotion Recognition Model (EERM) is a transformer-based Natural Language Processing (NLP) model developed for CTRL4 Chatbot MK II.

Its primary responsibility is to identify the emotional state expressed in a student's message before Retrieval-Augmented Generation (RAG) and Large Language Model (LLM) response generation.

Rather than generating chatbot responses directly, the model provides emotional context that enables the chatbot to produce more empathetic, supportive, and context-aware conversations.

---

# Model Information

| Property              | Value                             |
| --------------------- | --------------------------------- |
| Model Name            | English Emotion Recognition Model |
| Abbreviation          | EERM                              |
| Version               | 1.0                               |
| Base Model            | distilbert-base-uncased           |
| Architecture          | Transformer Encoder               |
| Framework             | Hugging Face Transformers         |
| Deep Learning Library | PyTorch                           |
| Task                  | Emotion Classification            |
| Language              | English                           |
| Output Classes        | 5                                 |

---

# Training Dataset

The model was fine-tuned using a merged English emotion dataset composed of multiple publicly available NLP datasets.

| Dataset          | Samples |
| ---------------- | ------: |
| GoEmotions       | 54,263  |
| ISEAR            |  7,102  |
| DAIR-AI Emotion  | 20,000  |
| **Total Samples**| **81,365** |

---

# Emotion Categories

| Label ID | Emotion  | Sentiment |
| --------:| -------- | --------- |
| 0         | Positive | Positive  |
| 1         | Neutral  | Neutral   |
| 2         | Anger    | Negative  |
| 3         | Sadness  | Negative  |
| 4         | Fear     | Negative  |

---

# Performance

| Metric     | Result |
| ---------- | -----: |
| Accuracy   | 79.45% |
| Precision  | 79.52% |
| Recall     | 79.45% |
| F1-Score   | 79.48% |

---

# Intended Use

The model is intended to support the CTRL4 AI pipeline through:

- Emotion detection
- Student guidance conversations
- Emotion-aware prompt construction
- Negative emotion recognition
- AI-assisted counseling support
- Context-aware response generation

---

# Not Intended For

The model should **not** be used for:

- Mental health diagnosis
- Clinical decision-making
- Psychological assessment
- Medical recommendations
- Independent crisis intervention
- Replacing licensed guidance counselors

The model serves only as a supporting component within the chatbot's AI pipeline.

---

# AI Pipeline Integration

The English Emotion Recognition Model operates as one component of the overall AI architecture.

```text
Student Message
        │
        ▼
Language Detection
        │
        ▼
English Emotion Model
        │
        ▼
Knowledge Retrieval (RAG)
        │
        ▼
Prompt Builder
        │
        ▼
Large Language Model
(Gemini / Ollama)
        │
        ▼
Generated Response
```

The predicted emotion is incorporated into the system prompt and provides contextual guidance for the language model.

---

# Current Limitations

The current model has several known limitations.

- Supports English only.
- Limited understanding of code-switched conversations.
- Does not interpret emojis.
- Limited recognition of internet slang.
- Predicts emotion independently for each message.
- Does not incorporate long-term conversation context.

---

# Planned Improvements

Future enhancements include:

- Filipino Emotion Recognition Model
- Taglish emotion recognition
- Code-switched language support
- Conversation-level emotion tracking
- Risk assessment integration
- Intent classification
- Larger counseling-specific datasets
- Improved confidence calibration

---

# Repository Location

```text
ai_engine/
└── models/
    └── english_emotion_model/
```

---

# Development Status

| Component             | Status                |
| --------------------- | :-------------------: |
| Training              | ✅ Completed          |
| Evaluation            | ✅ Completed          |
| Documentation         | ✅ Completed          |
| Backend Integration   | ✅ Integrated         |
| AI Pipeline           | ✅ Operational        |
| Production Deployment | 🚧 Local Development |

---

# License

This model was developed exclusively for the CTRL4 Chatbot MK II capstone project at Holy Angel University.

The implementation builds upon the open-source **DistilBERT** architecture provided by Hugging Face Transformers and utilizes publicly available emotion classification datasets for fine-tuning. Redistribution or commercial use should comply with the licensing terms of the original pretrained model and all datasets used during training.