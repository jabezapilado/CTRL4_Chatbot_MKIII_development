"""
English Emotion Recognition Model (EERM)

Interactive prediction script for the CTRL4 Chatbot MK2.

Author:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

import json
from pathlib import Path

import torch

from ai_engine.core.models.model_loader import load_model
from ai_engine.core.tokenizers.tokenizer import load_tokenizer


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

LABEL_ENCODER = PROJECT_ROOT / "configs" / "label_encoder.json"

with open(LABEL_ENCODER, "r", encoding="utf-8") as file:
    label_encoder = json.load(file)

LABELS = {
    int(index): emotion
    for emotion, index in label_encoder.items()
}

NEGATIVE_EMOTIONS = {
    "Anger",
    "Sadness",
    "Fear"
}


def main():

    print("=" * 60)
    print("CTRL4 CHATBOT MK2")
    print("ENGLISH EMOTION RECOGNITION MODEL")
    print("=" * 60)

    print("\nLoading tokenizer...")
    tokenizer = load_tokenizer("english")

    print("Loading model...")
    model = load_model("english")

    model.eval()

    print("Model loaded successfully.\n")

    while True:

        try:
            text = input("Student Message (type 'exit' to quit): ").strip()

            if text.lower() == "exit":
                print("\nGoodbye!")
                break

            if not text:
                print("Please enter a message.\n")
                continue

            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=128
            )

            with torch.no_grad():
                outputs = model(**inputs)

            probabilities = torch.softmax(outputs.logits, dim=1)[0]

            prediction = torch.argmax(probabilities).item()

            emotion = LABELS[prediction]
            confidence = probabilities[prediction].item()

            if emotion in NEGATIVE_EMOTIONS:
                sentiment = "Negative"
                is_negative = "Yes"
            elif emotion == "Positive":
                sentiment = "Positive"
                is_negative = "No"
            else:
                sentiment = "Neutral"
                is_negative = "No"

            print("\n" + "=" * 60)
            print("PREDICTION")
            print("=" * 60)

            print(f"Emotion      : {emotion}")
            print(f"Sentiment    : {sentiment}")
            print(f"Confidence   : {confidence:.2%}")
            print(f"Negative     : {is_negative}")

            print("\nEmotion Probabilities")
            print("-" * 60)

            for index, probability in enumerate(probabilities):
                print(
                    f"{LABELS[index]:<10} : {probability.item():.2%}"
                )

            print("=" * 60)
            print()

        except KeyboardInterrupt:
            print("\n\nPrediction cancelled.")
            break


if __name__ == "__main__":
    main()