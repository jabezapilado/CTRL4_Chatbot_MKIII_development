# CTRL4 Chatbot MK II
## 04 — Model Architecture

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

CTRL4 Chatbot MK II combines traditional machine learning with modern large language models to generate emotionally aware, context-aware, and institutionally accurate responses.

Instead of relying solely on a generative AI model, the chatbot first analyzes the student's message using several specialized artificial intelligence components before generating a response.

The primary machine learning model is a fine-tuned DistilBERT emotion classifier. Its predictions are combined with language detection, Retrieval-Augmented Generation (RAG), conversation history, and prompt engineering before the request is sent to the configured large language model.

This hybrid architecture improves response quality while reducing hallucinations and ensuring that official Guidance Office information remains accurate.

---

# Objectives

The AI model architecture was designed to achieve the following objectives:

- Detect the dominant emotion expressed in a student's message.
- Support emotionally appropriate response generation.
- Improve factual accuracy through Retrieval-Augmented Generation.
- Maintain fast inference suitable for real-time conversations.
- Separate machine learning inference from language model generation.
- Support multiple large language model providers.

---

# AI Model Architecture

CTRL4 Chatbot MK II consists of several independent AI models and services working together.

```text
Student Message
        │
        ▼
Safety Validation
        │
        ▼
Language Detection
        │
        ▼
DistilBERT Emotion Model
        │
        ▼
Knowledge Retrieval (RAG)
        │
        ▼
Prompt Construction
        │
        ▼
Large Language Model
(Gemini / Ollama)
        │
        ▼
Generated Response
```

Rather than replacing traditional NLP models, the language model builds upon the outputs produced by earlier AI components.

---

# DistilBERT Emotion Classifier

The emotion classifier is responsible for predicting the emotional context of each student message.

DistilBERT was selected because it provides an excellent balance between inference speed, memory efficiency, and classification performance.

The model is fine-tuned using a merged dataset consisting of multiple publicly available emotion classification datasets.

---

# Model Information

| Property               | Value                         |
| ---------------------- | ----------------------------- |
| Base Model             | distilbert-base-uncased       |
| Architecture           | Transformer Encoder           |
| Framework              | Hugging Face Transformers     |
| Deep Learning Library  | PyTorch                       |
| Task                   | Sequence Classification       |
| Output Labels          | 5 Emotion Classes             |
| Tokenizer              | DistilBERT Tokenizer          |

---

# Emotion Categories

The classifier predicts one of five standardized emotions.

| Label ID | Emotion  |
| --------:| -------- |
| 0         | Positive |
| 1         | Neutral  |
| 2         | Anger    |
| 3         | Sadness  |
| 4         | Fear     |

Each prediction also produces:

- Overall sentiment
- Confidence score
- Negative emotion indicator

These outputs are used as contextual information during prompt construction.

---

# Tokenization

Before inference, each student message is processed by the DistilBERT tokenizer.

The tokenizer performs:

- Text tokenization
- Input ID generation
- Attention mask generation
- Sequence padding
- Sequence truncation

The resulting tensors are passed to the transformer encoder for classification.

---

# Model Inference

The emotion prediction process follows the workflow below.

```text
Student Message
        │
        ▼
Tokenizer
        │
        ▼
Input IDs
Attention Mask
        │
        ▼
DistilBERT Encoder
        │
        ▼
Classification Head
        │
        ▼
Softmax
        │
        ▼
Emotion Prediction
Confidence Score
```

The highest-probability emotion becomes the primary prediction used by the chatbot.

---

# Model Configuration

The emotion classifier uses the following configuration.

| Parameter              | Value                        |
| ---------------------- | ---------------------------- |
| Base Model             | distilbert-base-uncased      |
| Maximum Sequence       | 128 Tokens                   |
| Number of Labels       | 5                            |
| Lowercase Text         | Yes                          |
| Output Type            | Sequence Classification      |

Configuration values are stored separately from the implementation to simplify experimentation and reproducibility.

---

# Training Configuration

The DistilBERT model was fine-tuned using supervised learning.

| Hyperparameter         | Value         |
| ---------------------- | ------------- |
| Optimizer              | AdamW         |
| Learning Rate          | 2e-5          |
| Batch Size             | 16            |
| Epochs                 | 5             |
| Weight Decay           | 0.01          |
| Evaluation Strategy    | Every Epoch   |
| Save Best Model        | Enabled       |
| Early Stopping         | Enabled       |

These settings provide a balance between convergence speed, training stability, and model generalization.

---

# Retrieval-Augmented Generation

The emotion model is only one part of the AI pipeline.

After emotion prediction, the chatbot retrieves verified Guidance Office information using Retrieval-Augmented Generation (RAG).

The retrieved knowledge provides factual context for the language model, reducing hallucinations and ensuring that institutional information remains accurate.

Typical retrieved information includes:

- Office hours
- Counseling services
- Appointment procedures
- Guidance Office policies
- Frequently Asked Questions

---

# Large Language Model Integration

The final chatbot response is generated by a configurable large language model provider.

Currently supported providers include:

- Google Gemini
- Ollama

The language model receives:

- Student message
- Conversation history
- Emotion prediction
- Language detection
- Retrieved Guidance Office knowledge
- System instructions
- Personality guidelines

The provider abstraction layer allows additional language models to be integrated without modifying the chatbot's business logic.

---

# Model Directory Structure

```text
ai_engine/

├── configs/
├── core/
│   ├── models/
│   ├── tokenizers/
│   ├── training/
│   └── utilities/
│
├── data/
├── knowledge_base/
└── models/
```

The trained DistilBERT model is stored independently from preprocessing scripts and training utilities, allowing deployment without retraining.

---

# Advantages

The hybrid AI architecture provides several advantages.

- Fast emotion inference
- Modular AI services
- Improved factual accuracy through RAG
- Reduced hallucinations
- Emotion-aware prompt construction
- Provider-independent LLM integration
- Easy scalability for future AI components

---

# Current Limitations

The current implementation has several limitations.

- Emotion datasets are primarily English.
- Code-switched emotion recognition remains limited.
- Conversation context is limited to recent messages.
- Institutional knowledge must be updated manually.
- Emotion prediction analyzes each message independently.

---

# Future Improvements

Planned enhancements include:

- Filipino and Tagalog emotion models
- Code-switched emotion detection
- Conversation-level emotion tracking
- Intent classification
- Risk prediction model
- Counselor analytics
- Improved multilingual support
- Fine-tuning using Guidance Office conversations

---

# Summary

The AI model architecture of CTRL4 Chatbot MK II combines transformer-based emotion classification with Retrieval-Augmented Generation and modern large language models to create a reliable, emotionally aware, and context-aware guidance assistant.

Rather than relying solely on generative AI, the system integrates specialized machine learning models, semantic knowledge retrieval, and prompt engineering to produce responses that are empathetic, institutionally accurate, and suitable for real-time student support.