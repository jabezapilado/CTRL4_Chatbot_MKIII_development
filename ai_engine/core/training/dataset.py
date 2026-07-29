"""
Dataset Preparation

Loads, encodes and tokenizes the merged emotion dataset.

Author: CTRL4 Chatbot MK2
"""

import json
from pathlib import Path

from datasets import load_from_disk

from ai_engine.core.tokenizers.tokenizer import load_tokenizer
from ai_engine.core.utilities.config import load_config


config = load_config("model_config.json")


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATASET_DIR = (
    PROJECT_ROOT
    / "data"
    / "merged"
    / "merged_emotion_dataset"
)

LABEL_ENCODER = (
    PROJECT_ROOT
    / "configs"
    / "label_encoder.json"
)


with open(
    LABEL_ENCODER,
    "r",
    encoding="utf-8"
) as file:

    label_encoder = json.load(file)


tokenizer = load_tokenizer()


def encode_labels(example):

    example["labels"] = label_encoder[
        example["emotion"]
    ]

    return example


def tokenize(example):

    return tokenizer(

        example["text"],

        truncation=True,

        padding="max_length",

        max_length=config["max_length"]

    )


def prepare_dataset():

    dataset = load_from_disk(
        DATASET_DIR
    )

    allowed_labels = set(label_encoder.keys())

    dataset = dataset.filter(
        lambda x: x["emotion"] in allowed_labels
    )

    dataset = dataset.map(
        encode_labels
    )

    dataset = dataset.map(
        tokenize,
        batched=True
    )

    dataset.set_format(

        type="torch",

        columns=[
            "input_ids",
            "attention_mask",
            "labels"
        ]

    )

    print()

    print("=" * 60)
    print("TRAINING DATASET")
    print("=" * 60)

    print(dataset)

    print()

    print("Train:", len(dataset["train"]))
    print("Validation:", len(dataset["validation"]))
    print("Test:", len(dataset["test"]))

    print("=" * 60)

    return dataset