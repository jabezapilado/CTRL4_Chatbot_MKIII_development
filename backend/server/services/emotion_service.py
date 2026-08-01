"""
Emotion Service

Loads and performs inference using the English Emotion
Recognition Model (EERM).

CTRL4 Chatbot MK2

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Final

import torch

from ai_engine.core.models.model_loader import load_model
from ai_engine.core.tokenizers.tokenizer import load_tokenizer


def _load_labels() -> dict[int, str]:
    project_root = Path(__file__).resolve().parents[3]
    encoder_path = project_root / "ai_engine" / "configs" / "label_encoder.json"

    with open(encoder_path, "r", encoding="utf-8") as handle:
        encoder = json.load(handle)

    return {
        int(index): emotion
        for emotion, index in encoder.items()
    }


LABELS: Final = _load_labels()

NEGATIVE_EMOTIONS: Final = {
    "Anger",
    "Sadness",
    "Fear",
}

POSITIVE_EMOTIONS: Final = {
    "Positive",
}

NEUTRAL_EMOTIONS: Final = {
    "Neutral",
}

@dataclass
class EmotionPrediction:
    emotion: str
    sentiment: str
    confidence: float
    is_negative: bool


class EmotionService:

    def __init__(self):

        self.tokenizer = load_tokenizer("english")
        self.model = load_model("english")

        self.model.eval()

    def normalize_emotion(
        self,
        text: str,
        emotion: str,
    ) -> str:

        text = text.lower()

        # Keep all outputs in the model's five-class taxonomy.
        # Stress/anxiety indicators are normalized to Fear.
        if any(word in text for word in [
            "stress",
            "stressed",
            "pressure",
            "burnout",
            "burned out",
            "overwhelmed",
            "exhausted",
            "drained",
            "mentally exhausted",
        ]):
            return "Fear"

        # Anxiety-related keywords
        if any(word in text for word in [
            "anxiety",
            "anxious",
            "panic",
            "nervous",
            "worried",
            "restless",
            "uneasy",
            "can't relax",
        ]):
            return "Fear"

        # Loneliness-related keywords are normalized to Sadness.
        if any(word in text for word in [
            "alone",
            "lonely",
            "isolated",
            "left out",
            "abandoned",
            "no one understands me",
        ]):
            return "Sadness"

        # Keep original model prediction
        return emotion
    
    def predict(self, text: str) -> EmotionPrediction:

        text = text.strip()

        if not text:
            raise ValueError("Text must not be empty.")

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )
        
        # DistilBERT does not use token_type_ids
        inputs.pop("token_type_ids", None)

        with torch.no_grad():
            outputs = self.model(**inputs)

        probabilities = torch.softmax(outputs.logits, dim=1)[0]

        prediction = torch.argmax(probabilities).item()

        emotion = LABELS[prediction]

        # Only refine neutral or negative predictions.
        # Avoid overriding a confident positive prediction
        # because of a single keyword.
        if emotion != "Positive":
            emotion = self.normalize_emotion(
                text,
                emotion,
            )

        confidence = probabilities[prediction].item()

        if emotion in NEGATIVE_EMOTIONS:
            sentiment = "Negative"
            is_negative = True

        elif emotion in POSITIVE_EMOTIONS:
            sentiment = "Positive"
            is_negative = False

        elif emotion in NEUTRAL_EMOTIONS:
            sentiment = "Neutral"
            is_negative = False

        else:
            sentiment = "Neutral"
            is_negative = False

        return EmotionPrediction(
            emotion=emotion,
            sentiment=sentiment,
            confidence=confidence,
            is_negative=is_negative,
        )