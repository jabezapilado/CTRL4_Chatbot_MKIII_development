"""
Emotion Model Training

Fine-tunes the emotion classification model.

Author: CTRL4 Chatbot MK2
"""

from ai_engine.core.training.dataset import prepare_dataset
from ai_engine.core.models.emotion_classifier import load_model
from ai_engine.core.tokenizers.tokenizer import load_tokenizer
from ai_engine.core.training.trainer import create_trainer
from ai_engine.core.utilities.config import load_config


config = load_config("model_config.json")


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


if __name__ == "__main__":
    main()