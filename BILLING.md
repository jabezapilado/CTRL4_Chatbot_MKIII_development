# Assumptions

> **Note**
>
> The cost estimates presented in this document are based on the official Google Gemini API pricing available at the time of writing and are intended for budgeting and deployment planning purposes only. Actual costs may vary depending on changes to API pricing, prompt length, response length, Retrieval-Augmented Generation (RAG) context size, conversation volume, and overall system usage. Always refer to the latest pricing published by the AI provider before estimating operational expenses.

| Parameter                                 | Value    |
| ----------------------------------------- | -------: |
| Deployment Duration                       | 4 Months |
| Active Students                           |      200 |
| Average Conversations per Student/Month   |       15 |
| Total Conversations                       |   12,000 |
| Average Input Tokens per Conversation     |    2,000 |
| Average Output Tokens per Conversation    |      500 |

---

# Gemini 2.5 Flash

## Pricing

| Token Type | Price                    |
| ---------- | -----------------------: |
| Input      | $0.30 / 1 Million Tokens |
| Output     | $2.50 / 1 Million Tokens |

## Estimated Cost

| Item   |      Tokens |         Rate |   Cost |
| ------ | ----------: | -----------: | -----: |
| Input  | 24,000,000  | $0.30 / 1M   |  $7.20 |
| Output |  6,000,000  | $2.50 / 1M   | $15.00 |

### Total Cost

| Currency      | Amount        |
| ------------- | ------------: |
| USD           | $22.20        |
| PHP (Approx.) | ₱1,250–₱1,350 |

---

# Gemini 2.5 Flash-Lite

## Pricing

| Token Type | Price                    |
| ---------- | -----------------------: |
| Input      | $0.10 / 1 Million Tokens |
| Output     | $0.40 / 1 Million Tokens |

## Estimated Cost

| Item   |      Tokens |         Rate |  Cost |
| ------ | ----------: | -----------: | ----: |
| Input  | 24,000,000  | $0.10 / 1M   | $2.40 |
| Output |  6,000,000  | $0.40 / 1M   | $2.40 |

### Total Cost

| Currency      | Amount |
| ------------- | -----: |
| USD           |  $4.80 |
| PHP (Approx.) | ₱270–₱300 |

---

# Cost Comparison

| Model                    | Total (USD) | Total (PHP Approx.) |
| ------------------------ | ----------: | ------------------: |
| Gemini 2.5 Flash         |      $22.20 |      ₱1,250–₱1,350  |
| Gemini 2.5 Flash-Lite    |       $4.80 |          ₱270–₱300  |

---

# High Usage Scenario

| Model                 | Estimated Cost (USD) | Estimated Cost (PHP Approx.) |
| --------------------- | -------------------: | ---------------------------: |
| Gemini 2.5 Flash      |               ~$59   |              ~₱3,300–₱3,600  |
| Gemini 2.5 Flash-Lite |               ~$13   |                  ~₱730–₱800  |

---

# Production Deployment

| Provider               | Recommended Use                      |
| ---------------------- | -------------------------------------|
| Gemini 2.5 Flash       | Best response quality                |
| Gemini 2.5 Flash-Lite  | Lowest cloud operating cost          |
| Ollama (Qwen2.5:7B)    | Fully local deployment (no API cost) |

---

# CTRL4 Cost Optimization

CTRL4 Chatbot employs a modular AI architecture that performs several Natural Language Processing (NLP) tasks locally before sending requests to the Large Language Model (LLM). These locally executed components include:

- Language Detection
- Emotion Detection
- Safety Validation
- Retrieval-Augmented Generation (RAG)
- Prompt Engineering

Because only the final, context-enriched prompt is sent to the LLM, token consumption is significantly reduced compared to systems that rely entirely on cloud-based language models. This architecture helps minimize operational costs while maintaining high-quality, context-aware responses.