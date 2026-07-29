"""
Emotion Classification Model

Loads DistilBERT for sequence classification.

Author: CTRL4 Chatbot MK2
"""

from transformers import AutoModelForSequenceClassification

from ai_engine.core.utilities.config import load_config


config = load_config("model_config.json")


def load_model():

    return AutoModelForSequenceClassification.from_pretrained(

        config["base_model"],

        num_labels=config["num_labels"]

    )