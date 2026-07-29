"""
Base Preprocessor

Shared preprocessing utilities for all datasets.

Author: CTRL4 Chatbot MK2
"""

from pathlib import Path
import json
import re

from datasets import DatasetDict

from ai_engine.core.schemas.emotion_record import EmotionRecord


class BasePreprocessor:
    """
    Base class for all dataset preprocessors.
    """

    def __init__(self, dataset_name: str):

        self.dataset_name = dataset_name

        # ai_engine/
        self.project_root = Path(__file__).resolve().parent.parent.parent

        self.config_dir = self.project_root / "configs"

        self.data_dir = self.project_root / "data"

        self.processed_dir = (
            self.data_dir
            / "processed"
            / dataset_name
        )

        self.processed_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.emotion_mapping = self.load_json(
            self.config_dir / "emotion_mapping.json"
        )

        self.sentiment_mapping = self.load_json(
            self.config_dir / "sentiment_mapping.json"
        )

    # ---------------------------------------------------------
    # Configuration
    # ---------------------------------------------------------

    def load_json(self, filepath: Path):

        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)

    # ---------------------------------------------------------
    # Text Processing
    # ---------------------------------------------------------

    def clean_text(self, text: str) -> str:

        if not isinstance(text, str):
            return ""

        text = text.strip()

        text = re.sub(r"\s+", " ", text)

        return text

    def validate_text(self, text: str) -> bool:

        if text is None:
            return False

        if len(text.strip()) == 0:
            return False

        return True

    # ---------------------------------------------------------
    # Emotion Mapping
    # ---------------------------------------------------------

    def map_emotion(self, original_emotion: str) -> str:

        return self.emotion_mapping.get(
            original_emotion.strip().lower(),
            "Neutral"
        )

    def map_sentiment(self, emotion: str):

        return self.sentiment_mapping.get(
            emotion,
            {
                "sentiment": "Neutral",
                "is_negative": False
            }
        )

    # ---------------------------------------------------------
    # Record Builder
    # ---------------------------------------------------------

    def generate_id(
        self,
        prefix: str,
        index: int
    ) -> str:

        return f"{prefix}_{index:06d}"

    def build_record(
        self,
        record_id: str,
        text: str,
        original_emotion: str,
        emotion: str,
        source: str
    ):

        text = self.clean_text(text)

        sentiment = self.map_sentiment(emotion)

        record = EmotionRecord(

            id=record_id,

            text=text,

            original_emotion=original_emotion,

            emotion=emotion,

            sentiment=sentiment["sentiment"],

            is_negative=sentiment["is_negative"],

            source=source

        )

        return record.to_dict()

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def validate_record(self, record) -> bool:

        required = [
            "id",
            "text",
            "emotion",
            "sentiment",
            "source"
        ]

        for key in required:

            if key not in record:
                return False

        return self.validate_text(record["text"])

    # ---------------------------------------------------------
    # Saving
    # ---------------------------------------------------------

    def save_dataset(self, dataset: DatasetDict):

        dataset.save_to_disk(
            self.processed_dir
        )

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def print_summary(
        self,
        train: int,
        validation: int,
        test: int
    ):

        total = train + validation + test

        print()

        print("=" * 60)

        print(f"{self.dataset_name.upper()} PREPROCESSING COMPLETE")

        print("=" * 60)

        print(f"Train       : {train:,}")

        print(f"Validation  : {validation:,}")

        print(f"Test        : {test:,}")

        print("-" * 60)

        print(f"Total       : {total:,}")

        print()

        print(f"Saved to: {self.processed_dir}")

        print("=" * 60)