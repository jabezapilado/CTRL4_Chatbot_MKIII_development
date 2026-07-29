"""
Merge Emotion Datasets

Combines all processed emotion datasets into one
training dataset.

Author: CTRL4 Chatbot MK2
"""

from datasets import (
    concatenate_datasets,
    DatasetDict,
    load_from_disk,
)

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "merged"
    / "merged_emotion_dataset"
)


DATASETS = [

    "goemotions",

    "isear",

    "dair_ai",

]


def load_all():

    train = []

    validation = []

    test = []

    for dataset_name in DATASETS:

        print(f"Loading {dataset_name}...")

        dataset = load_from_disk(
            PROCESSED_DIR / dataset_name
        )

        train.append(
            dataset["train"]
        )

        validation.append(
            dataset["validation"]
        )

        test.append(
            dataset["test"]
        )

    return (

        concatenate_datasets(train),

        concatenate_datasets(validation),

        concatenate_datasets(test),

    )


def remove_duplicates(dataset):

    seen = set()

    rows = []

    for row in dataset:

        text = row["text"].strip().lower()

        if text in seen:
            continue

        seen.add(text)

        rows.append(row)

    return dataset.from_list(rows)


def print_statistics(name, dataset):

    print()

    print(f"{name.upper()}")

    print("-" * 40)

    print(f"Samples : {len(dataset):,}")

    emotion_count = {}

    source_count = {}

    for row in dataset:

        emotion = row["emotion"]

        source = row["source"]

        emotion_count[emotion] = emotion_count.get(
            emotion,
            0
        ) + 1

        source_count[source] = source_count.get(
            source,
            0
        ) + 1

    print()

    print("Sources")

    for source, count in sorted(source_count.items()):

        print(f"  {source:<15} {count:,}")

    print()

    print("Emotions")

    for emotion, count in sorted(
        emotion_count.items(),
        key=lambda x: x[1],
        reverse=True,
    ):

        print(f"  {emotion:<15} {count:,}")


def main():

    train, validation, test = load_all()

    train = remove_duplicates(train)

    validation = remove_duplicates(validation)

    test = remove_duplicates(test)

    train = train.shuffle(seed=42)

    validation = validation.shuffle(seed=42)

    test = test.shuffle(seed=42)

    merged = DatasetDict({

        "train": train,

        "validation": validation,

        "test": test,

    })

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    merged.save_to_disk(
        OUTPUT_DIR
    )

    print()

    print("=" * 60)

    print("MERGED DATASET CREATED")

    print("=" * 60)

    print_statistics(
        "Train",
        train,
    )

    print_statistics(
        "Validation",
        validation,
    )

    print_statistics(
        "Test",
        test,
    )

    print()

    print("Saved to:")

    print(OUTPUT_DIR)


if __name__ == "__main__":

    main()