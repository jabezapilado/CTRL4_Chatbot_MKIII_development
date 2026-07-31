"""
Emotion Model Training

Fine-tunes the emotion classification model.

Author: CTRL4 Chatbot MK2
"""

import shutil
from pathlib import Path

from ai_engine.core.training.evaluate_model import main as evaluate_model
from ai_engine.core.training.dataset import prepare_dataset
from ai_engine.core.models.emotion_classifier import load_model
from ai_engine.core.tokenizers.tokenizer import load_tokenizer
from ai_engine.core.training.trainer import create_trainer
from ai_engine.core.utilities.config import load_config
import json
import os


config = load_config("model_config.json")


MODELS_DIR = Path("ai_engine/models")
LANGUAGE = "english"


def get_next_version():
    language_dir = MODELS_DIR / LANGUAGE
    language_dir.mkdir(parents=True, exist_ok=True)

    versions = []

    for folder in language_dir.iterdir():
        if folder.is_dir() and folder.name.startswith("v"):
            try:
                versions.append(int(folder.name[1:]))
            except ValueError:
                pass

    next_version = max(versions, default=0) + 1

    return language_dir / f"v{next_version}"


def copy_directory(source, destination):

    source = Path(source)
    destination = Path(destination)

    if destination.exists():
        shutil.rmtree(destination)

    shutil.copytree(source, destination)


def publish_model():

    output_dir = Path(config["output_dir"])

    version_dir = get_next_version()

    latest_dir = MODELS_DIR / LANGUAGE / "latest"

    print(f"\nPublishing model to {version_dir}")

    copy_directory(output_dir, version_dir)

    print("Updating latest model...")

    copy_directory(version_dir, latest_dir)

    return version_dir, latest_dir

def main():

    print()
    print("=" * 60)
    print("CTRL4 EMOTION MODEL TRAINING")
    print("=" * 60)

    print("\nPreparing dataset...")
    dataset = prepare_dataset()

    print("\nLoading tokenizer...")
    tokenizer = load_tokenizer()

    print("\nLoading model...")
    model = load_model()

    print("\nCreating trainer...")
    trainer = create_trainer(

        model=model,

        tokenizer=tokenizer,

        train_dataset=dataset["train"],

        validation_dataset=dataset["validation"]

    )

    print("\nStarting training...\n")

    trainer.train()

    print("\nEvaluating model...\n")

    metrics = trainer.evaluate()

    history_path = os.path.join(
        "docs",
        "models",
        "training_history.json"
    )

    os.makedirs(os.path.dirname(history_path), exist_ok=True)

    with open(history_path, "w") as f:
        json.dump(trainer.state.log_history, f, indent=4)

    print(f"Training history saved to {history_path}")

    print("=" * 60)
    print("FINAL METRICS")
    print("=" * 60)

    for key, value in metrics.items():
        print(f"{key:<25}{value}")

    print()

    trainer.save_model(
        config["output_dir"]
    )

    tokenizer.save_pretrained(
        config["output_dir"]
    )

    print("=" * 60)
    print("MODEL SAVED")
    print("=" * 60)
    print(config["output_dir"])

    version_dir, latest_dir = publish_model()

    print("\nRunning evaluation...\n")

    evaluate_model()

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Published Model : {version_dir}")
    print(f"Latest Model    : {latest_dir}")
    print("Evaluation      : docs/models/evaluation")


if __name__ == "__main__":
    main()