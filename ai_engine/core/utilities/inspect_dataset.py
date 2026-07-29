"""
Dataset Inspector

Displays useful information about a processed Hugging Face dataset.

Usage:
python -m ai_engine.core.utilities.inspect_dataset goemotions
python -m ai_engine.core.utilities.inspect_dataset isear

Author: CTRL4 Chatbot MK2
"""

import sys
from pathlib import Path

from datasets import load_from_disk


def print_split(name, dataset):

    print(f"{name:<12}: {len(dataset):,}")


def print_sample(sample):

    print("\n" + "=" * 60)
    print("SAMPLE RECORD")
    print("=" * 60)

    for key, value in sample.items():
        print(f"{key:20}: {value}")

    print("=" * 60)


def print_emotion_distribution(dataset):

    counts = {}

    for emotion in dataset["emotion"]:
        counts[emotion] = counts.get(emotion, 0) + 1

    print("\nEmotion Distribution")
    print("-" * 60)

    for emotion, count in sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        print(f"{emotion:20} {count:,}")


def main():

    if len(sys.argv) != 2:

        print("Usage:")
        print("python -m ai_engine.core.utilities.inspect_dataset <dataset_name>")
        return

    dataset_name = sys.argv[1]

    project_root = Path(__file__).resolve().parent.parent.parent

    dataset_path = (
        project_root
        / "data"
        / "processed"
        / dataset_name
    )

    dataset = load_from_disk(dataset_path)

    print()
    print("=" * 60)
    print(dataset_name.upper())
    print("=" * 60)

    print_split("Train", dataset["train"])
    print_split("Validation", dataset["validation"])
    print_split("Test", dataset["test"])

    total = (
        len(dataset["train"])
        + len(dataset["validation"])
        + len(dataset["test"])
    )

    print("-" * 60)
    print(f"{'Total':<12}: {total:,}")

    print_sample(dataset["train"][0])

    print_emotion_distribution(dataset["train"])


if __name__ == "__main__":

    main()