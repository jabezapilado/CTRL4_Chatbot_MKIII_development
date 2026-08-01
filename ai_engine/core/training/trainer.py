"""
Trainer Factory

Creates the Hugging Face Trainer.

Author: CTRL4 Chatbot MK2
"""

from transformers import (
    TrainingArguments,
    EarlyStoppingCallback,
)

from ai_engine.core.training.training_metrics_callback import TrainingMetricsCallback

from ai_engine.core.training.emotion_trainer import EmotionTrainer

from ai_engine.core.training.metrics import compute_metrics
from ai_engine.core.utilities.config import load_config


config = load_config("model_config.json")


def create_trainer(
    model,
    tokenizer,
    train_dataset,
    validation_dataset,
):

    training_metrics_callback = TrainingMetricsCallback()

    training_args = TrainingArguments(

        output_dir=config["output_dir"],

        learning_rate=config["learning_rate"],

        per_device_train_batch_size=config["batch_size"],

        per_device_eval_batch_size=config["batch_size"],

        num_train_epochs=config["epochs"],

        weight_decay=config["weight_decay"],

        warmup_ratio=config.get("warmup_ratio", 0.0),

        label_smoothing_factor=config.get("label_smoothing_factor", 0.0),

        eval_strategy=config["evaluation_strategy"],

        save_strategy=config["save_strategy"],

        logging_strategy="epoch",

        save_total_limit=2,

        report_to="none",

        seed=config["seed"],

        load_best_model_at_end=True,

        metric_for_best_model=config["best_model_metric"],

        greater_is_better=config["greater_is_better"],

    )

    trainer = EmotionTrainer(

        model=model,

        args=training_args,

        train_dataset=train_dataset,

        eval_dataset=validation_dataset,

        processing_class=tokenizer,

        compute_metrics=compute_metrics,

        callbacks=[
            training_metrics_callback,
            EarlyStoppingCallback(
                early_stopping_patience=config.get("early_stopping_patience", 1),
                early_stopping_threshold=config.get("early_stopping_threshold", 0.0),
            ),
        ],

    )

    training_metrics_callback.trainer = trainer

    return trainer