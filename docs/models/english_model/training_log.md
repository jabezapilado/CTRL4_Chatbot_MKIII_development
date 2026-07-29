# CTRL4 Chatbot MK II
## English Emotion Model Training Log

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

This document records the complete training process of the English Emotion Recognition Model (EERM) used in CTRL4 Chatbot MK II.

The model was fine-tuned using a merged English emotion dataset composed of GoEmotions, ISEAR, and DAIR-AI Emotion. Training was performed using the Hugging Face Transformers framework with PyTorch.

This document serves as a reproducible record of the model development process, including the training environment, dataset preparation, hyperparameters, checkpoints, and final evaluation results.

---

# Training Objectives

The training process was designed to:

- Fine-tune DistilBERT for multi-class emotion classification.
- Learn generalized emotional representations from multiple datasets.
- Produce a deployable emotion recognition model.
- Minimize validation loss while maximizing classification performance.
- Integrate the trained model into the CTRL4 AI pipeline.

---

# Model Information

| Property              | Value                             |
| --------------------- | --------------------------------- |
| Model Name            | English Emotion Recognition Model |
| Abbreviation          | EERM                              |
| Base Model            | distilbert-base-uncased           |
| Architecture          | Transformer Encoder               |
| Framework             | Hugging Face Transformers         |
| Deep Learning Library | PyTorch                           |
| Task                  | Emotion Classification            |
| Output Classes        | 5                                 |

---

# Training Dataset

### Source Datasets

| Dataset          | Samples |
| ---------------- | ------: |
| GoEmotions       | 54,263  |
| ISEAR            |  7,102  |
| DAIR-AI Emotion  | 20,000  |
| **Raw Total**    | **81,365** |

After preprocessing, validation, and removal of invalid records, the final dataset contained **80,975** samples.

### Dataset Split

| Dataset Split | Samples |
| ------------- | ------: |
| Training      | 64,551  |
| Validation    |  8,104  |
| Testing       |  8,107  |

---

# Training Environment

| Component             | Value                 |
| --------------------- | --------------------- |
| Operating System      | macOS                 |
| Python Version        | 3.13.5                |
| Deep Learning Library | PyTorch               |
| NLP Framework         | Hugging Face          |
| Compute Device        | Apple Silicon (MPS)   |

---

# Hyperparameters

| Hyperparameter       | Value       |
| -------------------- | ----------- |
| Optimizer            | AdamW       |
| Learning Rate        | 2e-5        |
| Batch Size           | 16          |
| Epochs               | 5           |
| Maximum Length       | 128         |
| Weight Decay         | 0.01        |
| Evaluation Strategy  | Every Epoch |
| Save Strategy        | Every Epoch |

---

# Training Progress

The English Emotion Recognition Model completed five training epochs.

Validation was performed after every epoch to monitor learning progress and evaluate generalization performance.

Intermediate checkpoints were generated automatically throughout training, allowing the best-performing model to be retained for deployment.

---

# Training Checkpoints

| Checkpoint        | Description                          |
| ----------------- | ------------------------------------ |
| checkpoint-12105  | Intermediate training checkpoint     |
| checkpoint-20175  | Final checkpoint before model export |

The final model was exported separately for deployment within the CTRL4 AI pipeline.

---

# Final Training Results

| Metric               | Value             |
| -------------------- | ----------------: |
| Training Epochs      | 5                 |
| Training Time        | 4 Hours 24 Minutes|
| Final Training Loss  | 0.3993            |
| Validation Accuracy  | 79.45%            |
| Precision            | 79.52%            |
| Recall               | 79.45%            |
| F1-Score             | 79.48%            |

---

# Training Observations

Several observations were recorded during the training process.

- Training loss decreased consistently across all epochs.
- Validation accuracy improved steadily during the early stages of training.
- Performance stabilized after several epochs, indicating convergence.
- Slight overfitting was observed near the end of training as validation performance plateaued while training loss continued to decrease.
- Overall model generalization remained stable and suitable for deployment within the chatbot.

---

# Generated Model Files

```text
ai_engine/
└── models/
    └── english_emotion_model/
        ├── config.json
        ├── model.safetensors
        ├── tokenizer.json
        ├── tokenizer_config.json
        ├── training_args.bin
        ├── checkpoint-12105/
        └── checkpoint-20175/
```

These files constitute Version 1 of the English Emotion Recognition Model.

---

# AI Pipeline Integration

The trained model is integrated into the CTRL4 AI pipeline through the `EmotionService`.

```text
Student Message
        │
        ▼
EmotionService
        │
        ▼
English Emotion Model
        │
        ▼
Emotion Prediction
        │
        ▼
Prompt Builder
        │
        ▼
Large Language Model
```

The predicted emotion is incorporated into the generated prompt, allowing the language model to produce more empathetic and context-aware responses.

---

# Development Status

| Component             | Status                |
| --------------------- | :-------------------: |
| Model Training        | ✅ Completed          |
| Tokenizer             | ✅ Completed          |
| Evaluation            | ✅ Completed          |
| Model Export          | ✅ Completed          |
| Backend Integration   | ✅ Integrated         |
| AI Pipeline           | ✅ Operational        |
| Production Deployment | 🚧 Local Development |

---

# Summary

The English Emotion Recognition Model was successfully fine-tuned using a merged dataset of publicly available English emotion classification corpora.

The resulting model achieved approximately **79.5% validation accuracy** while maintaining balanced precision, recall, and F1-score across five standardized emotion classes.

Within CTRL4 Chatbot MK II, the model functions as the emotion detection component of the AI pipeline. Its predictions provide contextual information that improves prompt construction and supports more empathetic, emotionally aware, and context-sensitive responses generated by the configured large language model.