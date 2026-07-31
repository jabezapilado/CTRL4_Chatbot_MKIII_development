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
from typing import Final

import torch

from ai_engine.core.models.model_loader import load_model
from ai_engine.core.tokenizers.tokenizer import load_tokenizer


LABELS: Final = {
    0: "Positive",
    1: "Neutral",
    2: "Anger",
    3: "Sadness",
    4: "Fear"
}

NEGATIVE_EMOTIONS: Final = {
    "Anger",
    "Sadness",
    "Fear",
    "Stress",
    "Anxiety",
    "Loneliness",
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

        # Stress-related keywords
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
            return "Stress"

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
            return "Anxiety"

        # Loneliness
        if any(word in text for word in [
            "alone",
            "lonely",
            "isolated",
            "left out",
            "abandoned",
            "no one understands me",
        ]):
            return "Loneliness"

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