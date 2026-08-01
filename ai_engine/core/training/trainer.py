"""
Trainer Factory

Creates the Hugging Face Trainer.

Author: CTRL4 Chatbot MK2
"""

from transformers import (
    TrainingArguments,
    EarlyStoppingCallback,
)
import numpy as np
import torch

from ai_engine.core.training.training_metrics_callback import TrainingMetricsCallback

from ai_engine.core.training.emotion_trainer import EmotionTrainer

from ai_engine.core.training.metrics import compute_metrics
from ai_engine.core.utilities.config import load_config


config = load_config("model_config.json")


def compute_class_weights(train_dataset, num_labels):
    labels = np.array(train_dataset["labels"], dtype=np.int64)

    if labels.size == 0:
        return None

    counts = np.bincount(labels, minlength=num_labels)
    total = counts.sum()

    weights = np.zeros(num_labels, dtype=np.float32)
    nonzero = counts > 0
    weights[nonzero] = total / (num_labels * counts[nonzero])

    # Keep average weight near 1.0 for stable optimization.
    if np.any(nonzero):
        weights[nonzero] = weights[nonzero] / weights[nonzero].mean()

    return torch.tensor(weights, dtype=torch.float32)


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

    class_weights = None
    if config.get("use_class_weights", True):
        class_weights = compute_class_weights(
            train_dataset,
            model.config.num_labels,
        )

    trainer = EmotionTrainer(

        model=model,

        args=training_args,

        train_dataset=train_dataset,

        eval_dataset=validation_dataset,

        processing_class=tokenizer,

        compute_metrics=compute_metrics,

        class_weights=class_weights,

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